const roomName = JSON.parse(document.getElementById('room-name').textContent);
const username = JSON.parse(document.getElementById('user-name').textContent);

const socket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/video/'
    + roomName
    + '/'
);

let localStream;
let mapPeers = {}; // Key: username, Value: [peerConnection, videoElement]

const config = {
    'iceServers': [
        { 'urls': 'stun:stun.l.google.com:19302' }
    ]
};

const localVideo = document.getElementById('local-video');
const videoGrid = document.querySelector('.video-container');

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
    }
};

async function startCall() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        localVideo.srcObject = localStream;

        document.getElementById('start-btn').style.display = 'none';
        document.getElementById('call-controls').style.display = 'flex'; // Show controls

        // Signal to others that I have joined
        sendSignal('new-peer', {});

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
        const [remoteStream] = event.streams;

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
    localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
    });

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
        const peerConnection = peerData[0];
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
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
            <line x1="12" y1="19" x2="12" y2="23"></line>
            <line x1="8" y1="23" x2="16" y2="23"></line>
        </svg>
        <span style="margin-left: 0.5rem;">Mute</span>`;
        btn.classList.remove('btn-danger'); // Assuming danger class for active state logic if added
        btn.classList.add('btn-secondary');
    } else {
        btn.innerHTML = `
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="1" y1="1" x2="23" y2="23"></line>
            <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"></path>
            <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"></path>
            <line x1="12" y1="19" x2="12" y2="23"></line>
            <line x1="8" y1="23" x2="16" y2="23"></line>
        </svg>
        <span style="margin-left: 0.5rem;">Unmute</span>`;
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
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 7l-7 5 7 5V7z"></path>
            <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
        </svg>
        <span style="margin-left: 0.5rem;">Stop Video</span>`;
    } else {
        btn.innerHTML = `
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 16v1a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h2m5.66 0H14a2 2 0 0 1 2 2v3.34l1 1L23 7v10"></path>
            <line x1="1" y1="1" x2="23" y2="23"></line>
        </svg>
        <span style="margin-left: 0.5rem;">Start Video</span>`;
    }
});

document.getElementById('hangup-btn').addEventListener('click', () => {
    // Close all connections
    for (const key in mapPeers) {
        mapPeers[key][0].close();
    }
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
    }
    window.location.href = '/dashboard/';
});
