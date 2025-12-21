document.addEventListener('DOMContentLoaded', function() {
    const sessionSlug = JSON.parse(document.getElementById('session-slug').textContent);
    const username = JSON.parse(document.getElementById('user-name').textContent);
    const isHost = JSON.parse(document.getElementById('is-host').textContent || 'false');
    const sessionType = JSON.parse(document.getElementById('session-type').textContent || '"regular"'); // Default to 'regular'
    const videoSessionId = document.getElementById('video-session-id') ? JSON.parse(document.getElementById('video-session-id').textContent) : null; // Only for regular sessions
    const breakoutSlugElement = document.getElementById('breakout-slug');
    const breakoutSlug = breakoutSlugElement ? JSON.parse(breakoutSlugElement.textContent) : null;

    // Construct WebSocket URL based on session type, main session, or breakout room
    let wsPath = 'ws://' + window.location.host + '/ws/video/' + sessionType + '/' + sessionSlug + '/';
    if (sessionType === 'regular' && breakoutSlug) {
        wsPath += 'breakout/' + breakoutSlug + '/';
    }

    const socket = new WebSocket(wsPath);
    console.log('WebSocket initiated with path:', wsPath);

    let localStream;
    let screenStream; // New global variable for screen share stream
    let mapPeers = {}; // Key: username, Value: [peerConnection, videoElement]

    const config = {
        'iceServers': [
            { 'urls': 'stun:stun.l.google.com:19302' }
        ]
    };

    const localVideo = document.getElementById('local-video');
    const videoGrid = document.querySelector('.video-grid'); // Changed from .video-container to .video-grid


socket.onmessage = async function (e) {
    const data = JSON.parse(e.data);
    const action = data['action'];
    const peerUsername = data['sender'];
    const payload = data['data'];

    if (peerUsername === username) {
        return;
    }

    if (action === 'new-peer') {
        createOffer(peerUsername);
    } else if (action === 'offer') {
        createAnswer(peerUsername, payload);
    } else if (action === 'answer') {
        addAnswer(peerUsername, payload);
    } else if (action === 'candidate') {
        addCandidate(peerUsername, payload);
    } else if (action === 'peer-disconnected') {
        removePeer(peerUsername);
    } else if (action === 'screen-share-started') {
        console.log(`${peerUsername} started screen sharing.`);
        // No explicit action here, the ontrack event will handle displaying the stream
    } else if (action === 'screen-share-stopped') {
        console.log(`${peerUsername} stopped screen sharing.`);
        // No explicit action here, the ontrack event will handle displaying the stream
    }
};

async function startCall() {
    console.log('startCall() function initiated.');
    try {
        console.log('Attempting to get user media...');
        localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        console.log('User media obtained successfully.');
        localVideo.srcObject = localStream;

        document.getElementById('start-btn').style.display = 'none';
        document.getElementById('call-controls').style.display = 'flex'; // Show controls
        document.getElementById('share-screen-btn').style.display = 'inline-flex'; // Show screen share button
        if (isHost) {
            document.getElementById('record-btn').style.display = 'inline-flex'; // Show record button if host
        }

        console.log('Sending new-peer signal...');
        // Signal to others that I have joined
        sendSignal('new-peer', {});
        console.log('New-peer signal sent.');

    } catch (error) {
        console.error('Error starting call:', error);
        alert('Could not access camera/microphone.');
    }
}

function createPeerConnection(peerUsername) {
    const peerConnection = new RTCPeerConnection(config);
    mapPeers[peerUsername] = [peerConnection, null];

    peerConnection.onicecandidate = function (event) {
        if (event.candidate) {
            sendSignal('candidate', event.candidate, peerUsername);
        }
    };

    peerConnection.ontrack = function (event) {
        const remoteStream = event.streams[0]; // event.streams is an array
        // Check if video element already exists for this peer
        let existingVideo = document.getElementById(`video-${peerUsername}`);
        if (!existingVideo) {
            existingVideo = createRemoteVideoElement(peerUsername);
        }
        existingVideo.srcObject = remoteStream;
    };

    peerConnection.onconnectionstatechange = function () {
        if (peerConnection.connectionState === 'disconnected' || peerConnection.connectionState === 'failed') {
            removePeer(peerUsername);
        }
    }

    // Add local tracks
    if (localStream) {
        localStream.getTracks().forEach(track => {
            peerConnection.addTrack(track, localStream);
        });
    }
    // If screenStream is active, also add its tracks
    if (screenStream) {
        screenStream.getTracks().forEach(track => {
            peerConnection.addTrack(track, screenStream);
        });
    }

    return peerConnection;
}

function createRemoteVideoElement(peerUsername) {
    const wrapper = document.createElement('div');
    wrapper.className = 'video-wrapper';
    wrapper.id = `wrapper-${peerUsername}`;
    wrapper.style.cssText = 'position: relative; background: #000; border-radius: 1rem; overflow: hidden; aspect-ratio: 16/9; animation: fadeIn 0.5s;';

    const video = document.createElement('video');
    video.id = `video-${peerUsername}`;
    video.autoplay = true;
    video.playsInline = true;
    video.style.cssText = 'width: 100%; height: 100%; object-fit: cover;';

    const label = document.createElement('div');
    label.innerText = peerUsername;
    label.style.cssText = 'position: absolute; bottom: 10px; left: 10px; background: rgba(0,0,0,0.5); padding: 5px 10px; border-radius: 5px; color: white; font-size: 0.8rem;';

    wrapper.appendChild(video);
    wrapper.appendChild(label);
    videoGrid.appendChild(wrapper);

    return video;
}

async function createOffer(peerUsername) {
    const peerConnection = createPeerConnection(peerUsername);
    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);
    sendSignal('offer', offer, peerUsername);
}

async function createAnswer(peerUsername, offer) {
    const peerConnection = createPeerConnection(peerUsername);
    await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);
    sendSignal('answer', answer, peerUsername);
}

async function addAnswer(peerUsername, answer) {
    const peerData = mapPeers[peerUsername];
    if (peerData) {
        const peerConnection = peerData[0];
        await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
    }
}

async function addCandidate(peerUsername, candidate) {
    const peerData = mapPeers[peerUsername];
    if (peerData) {
        const peerConnection = peerData[0];
        await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
    }
}

function removePeer(peerUsername) {
    const peerData = mapPeers[peerUsername];
    if (peerData) {
        const peerConnection = mapPeers[peerUsername][0];
        peerConnection.close();
        delete mapPeers[peerUsername];
    }
    const wrapper = document.getElementById(`wrapper-${peerUsername}`);
    if (wrapper) {
        wrapper.remove();
    }
}

function sendSignal(action, data, targetUsername = null) {
    socket.send(JSON.stringify({
        'action': action,
        'data': data,
        'target': targetUsername
    }));
}

document.getElementById('start-btn').addEventListener('click', startCall);

// Toggle Audio
let audioEnabled = true;
document.getElementById('toggle-audio-btn').addEventListener('click', () => {
    audioEnabled = !audioEnabled;
    localStream.getAudioTracks()[0].enabled = audioEnabled;
    const btn = document.getElementById('toggle-audio-btn');
    if (audioEnabled) {
        btn.innerHTML = `
        <i class="fas fa-microphone"></i>
        <span class="ms-2">Mute</span>`;
        btn.classList.remove('btn-danger'); // Assuming danger class for active state logic if added
        btn.classList.add('btn-secondary');
    } else {
        btn.innerHTML = `
        <i class="fas fa-microphone-slash"></i>
        <span class="ms-2">Unmute</span>`;
        btn.classList.remove('btn-secondary');
        // btn.classList.add('btn-danger'); // Optional style
    }
});

// Toggle Video
let videoEnabled = true;
document.getElementById('toggle-video-btn').addEventListener('click', () => {
    videoEnabled = !videoEnabled;
    localStream.getVideoTracks()[0].enabled = videoEnabled;
    const btn = document.getElementById('toggle-video-btn');
    if (videoEnabled) {
        btn.innerHTML = `
        <i class="fas fa-video"></i>
        <span class="ms-2">Stop Video</span>`;
    } else {
        btn.innerHTML = `
        <i class="fas fa-video-slash"></i>
        <span class="ms-2">Start Video</span>`;
    }
});

// Screen Share Functionality
let screenSharing = false;
const shareScreenBtn = document.getElementById('share-screen-btn');

shareScreenBtn.addEventListener('click', () => {
    if (screenSharing) {
        stopScreenShare();
    } else {
        startScreenShare();
    }
});

async function startScreenShare() {
    try {
        screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: false });
        
        // Update local video element to show screen share
        localVideo.srcObject = screenStream;

        // Replace video track for all peer connections
        for (const peerUsername in mapPeers) {
            const peerConnection = mapPeers[peerUsername][0];
            const videoSender = peerConnection.getSenders().find(sender => sender.track.kind === 'video');
            if (videoSender) {
                await videoSender.replaceTrack(screenStream.getVideoTracks()[0]);
            } else {
                // If no video sender, add the track (e.g., if only audio was shared initially)
                peerConnection.addTrack(screenStream.getVideoTracks()[0], screenStream);
            }
        }
        
        screenStream.getVideoTracks()[0].onended = () => {
            stopScreenShare();
        };

        screenSharing = true;
        shareScreenBtn.innerHTML = '<i class="fas fa-stop-circle"></i> <span class="ms-2">Stop Share</span>';
        shareScreenBtn.classList.add('btn-warning');
        shareScreenBtn.classList.remove('btn-secondary');

        sendSignal('screen-share-started', {});

    } catch (error) {
        console.error('Error starting screen share:', error);
        alert('Could not start screen sharing.');
        stopScreenShare(); // Ensure UI reverts if screen share fails
    }
}

async function stopScreenShare() {
    if (screenStream) {
        screenStream.getTracks().forEach(track => track.stop());
    }

    // Replace screen track with camera track (if camera was active)
    if (localStream) {
        localVideo.srcObject = localStream;
        for (const peerUsername in mapPeers) {
            const peerConnection = mapPeers[peerUsername][0];
            const videoSender = peerConnection.getSenders().find(sender => sender.track.kind === 'video');
            if (videoSender) {
                await videoSender.replaceTrack(localStream.getVideoTracks()[0]);
            }
        }
    } else {
        // If no localStream (e.g., user started call with only screen share),
        // we might need to remove the track or handle it differently.
        // For simplicity, this assumes localStream was started first.
        for (const peerUsername in mapPeers) {
            const peerConnection = mapPeers[peerUsername][0];
            const videoSender = peerConnection.getSenders().find(sender => sender.track.kind === 'video');
            if (videoSender) {
                // A more robust solution might remove the sender or replace with a black video track
                videoSender.replaceTrack(null); 
            }
        }
    }

    screenSharing = false;
    shareScreenBtn.innerHTML = '<i class="fas fa-desktop"></i> <span class="ms-2">Share Screen</span>';
    shareScreenBtn.classList.remove('btn-warning');
    shareScreenBtn.classList.add('btn-secondary');

    sendSignal('screen-share-stopped', {});
}


// Recording Functionality
let isRecording = false;
let currentRecordingId = null;
const recordBtn = document.getElementById('record-btn');
const recordingsList = document.getElementById('recordings-list'); // Assuming this element exists

if (isHost && recordBtn && sessionType === 'regular') { // Ensure record button exists and user is host
    recordBtn.addEventListener('click', () => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');


async function startRecording() {
    try {
        const response = await fetch('/videoconference/api/recording/start/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken,
            },
            body: new URLSearchParams({
                'session_id': videoSessionId
            })
        });
        const data = await response.json();
        if (response.ok) {
            isRecording = true;
            currentRecordingId = data.recording_id;
            recordBtn.innerHTML = '<i class="fas fa-stop"></i> <span class="ms-2">Stop Recording</span>';
            recordBtn.classList.remove('btn-danger');
            recordBtn.classList.add('btn-warning');
            alert('Recording started!');
            loadRecordings(); // Refresh recordings list
        } else {
            alert(`Error starting recording: ${data.error}`);
        }
    } catch (error) {
        console.error('Network error starting recording:', error);
        alert('Failed to start recording due to network error.');
    }
}

async function stopRecording() {
    try {
        const response = await fetch('/videoconference/api/recording/stop/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken,
            },
            body: new URLSearchParams({
                'recording_id': currentRecordingId
            })
        });
        const data = await response.json();
        if (response.ok) {
            isRecording = false;
            currentRecordingId = null;
            recordBtn.innerHTML = '<i class="fas fa-video"></i> <span class="ms-2">Record</span>';
            recordBtn.classList.remove('btn-warning');
            recordBtn.classList.add('btn-danger');
            alert('Recording stopped!');
            loadRecordings(); // Refresh recordings list
        } else {
            alert(`Error stopping recording: ${data.error}`);
        }
    } catch (error) {
        console.error('Network error stopping recording:', error);
        alert('Failed to stop recording due to network error.');
    }
}

// Function to load and display recordings
async function loadRecordings() {
    // This API endpoint needs to be created in views.py and urls.py
    try {
        const response = await fetch(`/videoconference/api/recordings/list/?session_id=${videoSessionId}`);
        const data = await response.json();

        if (response.ok) {
            recordingsList.innerHTML = ''; // Clear previous list
            if (data.recordings && data.recordings.length > 0) {
                data.recordings.forEach(recording => {
                    const li = document.createElement('li');
                    li.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');
                    
                    let title = recording.title || `Recording from ${new Date(recording.start_time).toLocaleString()}`;
                    li.innerHTML = `
                        <span>${title}</span>
                        ${recording.file_url ? `<a href="${recording.file_url}" target="_blank" class="btn btn-sm btn-outline-primary ms-auto">Play</a>` : ''}
                    `;
                    recordingsList.appendChild(li);
                });
            } else {
                recordingsList.innerHTML = '<li class="list-group-item">No recordings yet.</li>';
            }
        } else {
            console.error('Error listing recordings:', data.error);
        }
    } catch (error) {
        console.error('Network error listing recordings:', error);
    }
}

// Initial load of recordings on page load
// document.addEventListener('DOMContentLoaded', loadRecordings); // This is already in the inline script below


// Attendance Functionality
const refreshAttendanceBtn = document.getElementById('refresh-attendance-btn');
const attendanceList = document.getElementById('attendance-list');

if (isHost && refreshAttendanceBtn) {
    refreshAttendanceBtn.addEventListener('click', loadAttendance);
}

async function loadAttendance() {
    try {
        const response = await fetch(`/videoconference/api/attendance/list/?session_id=${videoSessionId}`);
        const data = await response.json();

        if (response.ok) {
            attendanceList.innerHTML = ''; // Clear previous list
            if (data.attendance && data.attendance.length > 0) {
                data.attendance.forEach(participant => {
                    const li = document.createElement('li');
                    li.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');
                    
                    let status = participant.left_at ? `Left: ${new Date(participant.left_at).toLocaleTimeString()}` : 'Joined';
                    let roomInfo = participant.breakout_room ? ` (${participant.breakout_room})` : '';

                    li.innerHTML = `
                        <span>${participant.username} ${roomInfo}</span>
                        <small class="text-muted ms-auto">${status} at ${new Date(participant.joined_at).toLocaleTimeString()}</small>
                    `;
                    attendanceList.appendChild(li);
                });
            } else {
                attendanceList.innerHTML = '<li class="list-group-item">No attendance data yet.</li>';
            }
        } else {
            console.error('Error listing attendance:', data.error);
        }
    } catch (error) {
        console.error('Network error listing attendance:', error);
    }
}
