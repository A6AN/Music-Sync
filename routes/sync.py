"""
Sync routes: handle playlist and liked songs syncing between services
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response, stream_with_context
from flask_login import login_required, current_user
import json
import time

bp = Blueprint('sync', __name__, url_prefix='/sync')


@bp.route('/spotify-to-ytmusic')
@login_required
def spotify_to_ytmusic():
    """Page for syncing Spotify → YouTube Music"""
    from flask import current_app
    SpotifyCredentials = current_app.SpotifyCredentials
    YTMusicCredentials = current_app.YTMusicCredentials
    
    spotify_creds = SpotifyCredentials.query.filter_by(user_id=current_user.id).first()
    ytmusic_creds = YTMusicCredentials.query.filter_by(user_id=current_user.id).first()
    
    if not spotify_creds or not spotify_creds.is_valid():
        flash('Please connect your Spotify account first', 'warning')
        return redirect(url_for('spotify.auth'))
    
    if not ytmusic_creds:
        flash('Please connect your YouTube Music account first', 'warning')
        return redirect(url_for('ytmusic.auth'))
    
    return render_template('sync/spotify_to_ytmusic.html')


@bp.route('/ytmusic-to-spotify')
@login_required
def ytmusic_to_spotify():
    """Page for syncing YouTube Music → Spotify"""
    from flask import current_app
    SpotifyCredentials = current_app.SpotifyCredentials
    YTMusicCredentials = current_app.YTMusicCredentials
    
    spotify_creds = SpotifyCredentials.query.filter_by(user_id=current_user.id).first()
    ytmusic_creds = YTMusicCredentials.query.filter_by(user_id=current_user.id).first()
    
    if not spotify_creds or not spotify_creds.is_valid():
        flash('Please connect your Spotify account first', 'warning')
        return redirect(url_for('spotify.auth'))
    
    if not ytmusic_creds:
        flash('Please connect your YouTube Music account first', 'warning')
        return redirect(url_for('ytmusic.auth'))
    
    return render_template('sync/ytmusic_to_spotify.html')


@bp.route('/history')
@login_required
def history():
    """View sync history"""
    from flask import current_app
    SyncHistory = current_app.SyncHistory
    
    history = SyncHistory.query.filter_by(user_id=current_user.id).order_by(
        SyncHistory.started_at.desc()
    ).limit(50).all()
    
    return render_template('sync/history.html', history=history)


@bp.route('/start')
@login_required
def start_sync():
    """Start playlist sync with Server-Sent Events for progress"""
    from flask import current_app
    from spotify2ytmusic import backend
    from ytmusicapi import YTMusic
    import requests
    
    playlist_id = request.args.get('playlist_id')
    new_playlist_name = request.args.get('name', '')
    algo = int(request.args.get('algo', 1))
    
    SpotifyCredentials = current_app.SpotifyCredentials
    YTMusicCredentials = current_app.YTMusicCredentials
    db = current_app.db
    SyncHistory = current_app.SyncHistory
    
    spotify_creds = SpotifyCredentials.query.filter_by(user_id=current_user.id).first()
    ytmusic_creds = YTMusicCredentials.query.filter_by(user_id=current_user.id).first()
    
    def generate():
        sync_record = None
        try:
            # Initialize YTMusic
            yield f"data: {json.dumps({'status': 'Initializing YouTube Music...', 'percent': 5})}\n\n"
            ytmusic = YTMusic(auth=ytmusic_creds.get_headers())
            
            # Fetch Spotify playlist
            yield f"data: {json.dumps({'status': 'Fetching Spotify playlist...', 'percent': 10})}\n\n"
            headers = {'Authorization': f'Bearer {spotify_creds.access_token}'}
            pl_response = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id}', headers=headers)
            
            if pl_response.status_code != 200:
                yield f"event: error\ndata: {json.dumps({'message': 'Failed to fetch playlist'})}\n\n"
                return
            
            playlist = pl_response.json()
            playlist_name = new_playlist_name if new_playlist_name else playlist['name']
            
            # Create sync history record
            sync_record = SyncHistory(
                user_id=current_user.id,
                sync_type='playlist',
                direction='spotify_to_ytmusic',
                playlist_name=playlist_name,
                source_id=playlist_id,
                status='running'
            )
            db.session.add(sync_record)
            db.session.commit()
            
            total_tracks = playlist['tracks']['total']
            yield f"data: {json.dumps({'status': f'Found {total_tracks} tracks', 'percent': 15})}\n\n"
            
            # Fetch all tracks
            tracks = []
            url = playlist['tracks']['href']
            while url:
                response = requests.get(url, headers=headers)
                data = response.json()
                tracks.extend(data['items'])
                url = data.get('next')
                percent = 15 + (len(tracks) / total_tracks * 10)
                yield f"data: {json.dumps({'status': f'Loading tracks: {len(tracks)}/{total_tracks}', 'percent': percent})}\n\n"
            
            # Update total tracks
            sync_record.tracks_total = total_tracks
            db.session.commit()
            
            # Create YouTube Music playlist
            yield f"data: {json.dumps({'status': 'Creating YouTube Music playlist...', 'percent': 30})}\n\n"
            yt_playlist_id = ytmusic.create_playlist(playlist_name, f'Synced from Spotify')
            sync_record.destination_id = yt_playlist_id
            db.session.commit()
            
            # Sync tracks
            synced = 0
            failed = 0
            for i, item in enumerate(tracks):
                if not item or not item.get('track'):
                    continue
                    
                track = item['track']
                track_name = track['name']
                artist_name = track['artists'][0]['name'] if track['artists'] else ''
                
                percent = 30 + ((i + 1) / total_tracks * 65)
                yield f"data: {json.dumps({'status': f'Syncing: {track_name} - {artist_name}', 'percent': percent, 'message': f'{i+1}/{total_tracks}: {track_name}'})}\n\n"
                
                try:
                    # Search on YouTube Music
                    query = f'{track_name} {artist_name}'
                    search_results = ytmusic.search(query, filter='songs', limit=5)
                    
                    if search_results:
                        video_id = search_results[0]['videoId']
                        ytmusic.add_playlist_items(yt_playlist_id, [video_id])
                        synced += 1
                    else:
                        failed += 1
                        yield f"data: {json.dumps({'message': f'Not found: {track_name}', 'type': 'danger'})}\n\n"
                except Exception as e:
                    failed += 1
                    yield f"data: {json.dumps({'message': f'Error: {track_name} - {str(e)}', 'type': 'danger'})}\n\n"
            
            # Complete - update sync record
            if sync_record:
                sync_record.status = 'completed'
                sync_record.tracks_synced = synced
                sync_record.tracks_failed = failed
                sync_record.completed_at = db.func.now()
                db.session.commit()
            
            yield f"event: complete\ndata: {json.dumps({'status': f'Complete! {synced} synced, {failed} failed', 'percent': 100, 'message': 'Sync completed successfully!', 'type': 'success'})}\n\n"
            
        except Exception as e:
            if sync_record:
                sync_record.status = 'failed'
                sync_record.error_message = str(e)
                sync_record.completed_at = db.func.now()
                db.session.commit()
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@bp.route('/start-ytmusic-to-spotify')
@login_required
def start_ytmusic_to_spotify():
    """Start YouTube Music to Spotify sync with Server-Sent Events for progress"""
    from flask import current_app
    from ytmusicapi import YTMusic
    import requests
    
    playlist_id = request.args.get('playlist_id')
    new_playlist_name = request.args.get('name', '')
    
    SpotifyCredentials = current_app.SpotifyCredentials
    YTMusicCredentials = current_app.YTMusicCredentials
    db = current_app.db
    SyncHistory = current_app.SyncHistory
    
    spotify_creds = SpotifyCredentials.query.filter_by(user_id=current_user.id).first()
    ytmusic_creds = YTMusicCredentials.query.filter_by(user_id=current_user.id).first()
    
    def generate():
        sync_record = None
        try:
            # Initialize services
            yield f"data: {json.dumps({'status': 'Initializing services...', 'percent': 5})}\n\n"
            ytmusic = YTMusic(auth=ytmusic_creds.get_headers())
            
            # Fetch YouTube Music playlist
            yield f"data: {json.dumps({'status': 'Fetching YouTube Music playlist...', 'percent': 10})}\n\n"
            playlist = ytmusic.get_playlist(playlist_id, limit=None)
            
            if not playlist:
                yield f"event: error\ndata: {json.dumps({'message': 'Failed to fetch playlist'})}\n\n"
                return
            
            playlist_name = new_playlist_name if new_playlist_name else playlist['title']
            tracks = playlist.get('tracks', [])
            total_tracks = len(tracks)
            
            # Create sync history record
            sync_record = SyncHistory(
                user_id=current_user.id,
                sync_type='playlist',
                direction='ytmusic_to_spotify',
                playlist_name=playlist_name,
                source_id=playlist_id,
                tracks_total=total_tracks,
                status='running'
            )
            db.session.add(sync_record)
            db.session.commit()
            
            yield f"data: {json.dumps({'status': f'Found {total_tracks} tracks', 'percent': 15})}\n\n"
            
            # Create Spotify playlist
            yield f"data: {json.dumps({'status': 'Creating Spotify playlist...', 'percent': 20})}\n\n"
            headers = {
                'Authorization': f'Bearer {spotify_creds.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get user ID
            user_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
            if user_response.status_code != 200:
                error_msg = f'Failed to get Spotify user info (Status {user_response.status_code})'
                try:
                    error_data = user_response.json()
                    error_msg += f': {error_data.get("error", {}).get("message", "")}'
                except:
                    pass
                yield f"event: error\ndata: {json.dumps({'message': error_msg})}\n\n"
                return
            
            spotify_user_id = user_response.json()['id']
            
            # Create playlist
            create_response = requests.post(
                f'https://api.spotify.com/v1/users/{spotify_user_id}/playlists',
                headers=headers,
                json={
                    'name': playlist_name,
                    'description': 'Synced from YouTube Music',
                    'public': False
                }
            )
            
            if create_response.status_code not in [200, 201]:
                error_msg = f'Failed to create Spotify playlist (Status {create_response.status_code})'
                try:
                    error_data = create_response.json()
                    error_msg += f': {error_data.get("error", {}).get("message", "")}'
                except:
                    error_msg += f' - Response: {create_response.text[:200]}'
                yield f"event: error\ndata: {json.dumps({'message': error_msg})}\n\n"
                return
            
            spotify_playlist_id = create_response.json()['id']
            sync_record.destination_id = spotify_playlist_id
            db.session.commit()
            
            # Sync tracks
            synced = 0
            failed = 0
            track_uris = []
            
            for i, track in enumerate(tracks):
                if not track:
                    continue
                
                track_title = track.get('title', '')
                artists = track.get('artists', [])
                artist_name = artists[0]['name'] if artists else ''
                
                percent = 25 + ((i + 1) / total_tracks * 70)
                yield f"data: {json.dumps({'status': f'Syncing: {track_title} - {artist_name}', 'percent': percent, 'message': f'{i+1}/{total_tracks}: {track_title}'})}\n\n"
                
                try:
                    # Search on Spotify
                    query = f'{track_title} {artist_name}'
                    search_response = requests.get(
                        'https://api.spotify.com/v1/search',
                        headers=headers,
                        params={'q': query, 'type': 'track', 'limit': 5}
                    )
                    
                    if search_response.status_code == 200:
                        results = search_response.json().get('tracks', {}).get('items', [])
                        if results:
                            track_uris.append(results[0]['uri'])
                            synced += 1
                            
                            # Add tracks in batches of 100
                            if len(track_uris) >= 100:
                                requests.post(
                                    f'https://api.spotify.com/v1/playlists/{spotify_playlist_id}/tracks',
                                    headers=headers,
                                    json={'uris': track_uris}
                                )
                                track_uris = []
                        else:
                            failed += 1
                            yield f"data: {json.dumps({'message': f'Not found: {track_title}', 'type': 'warning'})}\n\n"
                    else:
                        failed += 1
                        
                except Exception as e:
                    failed += 1
                    yield f"data: {json.dumps({'message': f'Error: {track_title} - {str(e)}', 'type': 'danger'})}\n\n"
            
            # Add remaining tracks
            if track_uris:
                requests.post(
                    f'https://api.spotify.com/v1/playlists/{spotify_playlist_id}/tracks',
                    headers=headers,
                    json={'uris': track_uris}
                )
            
            # Complete - update sync record
            if sync_record:
                sync_record.status = 'completed'
                sync_record.tracks_synced = synced
                sync_record.tracks_failed = failed
                sync_record.completed_at = db.func.now()
                db.session.commit()
            
            yield f"event: complete\ndata: {json.dumps({'status': f'Complete! {synced} synced, {failed} failed', 'percent': 100, 'message': 'Sync completed successfully!', 'type': 'success'})}\n\n"
            
        except Exception as e:
            if sync_record:
                sync_record.status = 'failed'
                sync_record.error_message = str(e)
                sync_record.completed_at = db.func.now()
                db.session.commit()
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')
