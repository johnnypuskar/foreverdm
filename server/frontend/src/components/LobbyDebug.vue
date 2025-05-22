<template>
<div class="flex flex-row justify-center items-center h-screen">
    <div class="flex flex-col">
        <p class="text-2xl mb-4 text-center">Lobby Debug</p>
        <input type="text" v-model="playerId" placeholder="Set Player ID" class="border border-gray-300 rounded p-2 m-2">

        </input>
        <div>
            <button @click="joinLobby" class="bg-blue-500 hover:bg-blue-700 active:bg-blue-900 text-white font-bold py-2 px-4 rounded m-2 cursor-pointer">
                Join Lobby
            </button>
            <input type="text" v-model="lobbyId" placeholder="Enter Lobby ID" class="border border-gray-300 rounded p-2 m-2"/>
        </div>
        <div>
            <span class="font-bold">Current Lobby: </span>
            <span class="text-gray-700">{{ activeLobbyId }}</span>
        </div>
        <button @click="leaveLobby" class="bg-green-500 hover:bg-green-700 active:bg-green-900 text-white font-bold py-2 px-4 rounded m-2 cursor-pointer">
            Leave Lobby
        </button>
        <button @click="debugData" class="bg-red-500 hover:bg-red-700 active:bg-red-900 text-white font-bold py-2 px-4 rounded m-2 cursor-pointer">
            Get Debug Data
        </button>
    </div>
    <div>
        <p>Debug Log</p>
        <div class="debugLog border border-gray-300 rounded p-2 m-2 h-64 overflow-y-auto min-w-160">
            <ul>
                <li v-for="log in debugLog" :key="log" class="text-gray-700">
                    {{ log }}
                </li>
            </ul>
        </div>
    </div>
</div>
</template>

<script lang="ts" setup>
import { nextTick, ref, inject, onBeforeUnmount, onMounted } from 'vue';
import { VueCookies } from 'vue-cookies';
import { io } from 'socket.io-client';

const $cookies = inject<VueCookies>('$cookies');

const playerId = ref('');
const lobbyId = ref('');
const debugLog = ref([]);

const socket = io('http://localhost:5000');
const activeLobbyId = ref('');

function log(message: string) {
    debugLog.value.push("> " + message);
    nextTick(() => {
        const logDiv = document.querySelector('.debugLog');
        if (logDiv) {
            logDiv.scrollTop = logDiv.scrollHeight;
        }
    });
}

function joinLobby() {
    lobbyId.value = lobbyId.value.trim();
    if (lobbyId.value === '') {
        log("Failed lobby join attempt: empty lobby ID");
        return;
    }
    if (playerId.value === '') {
        log("Failed lobby join attempt: empty player ID");
        return;
    }
    socket.emit('join', lobbyId.value, playerId.value);

    lobbyId.value = "";
}

function leaveLobby() {
    socket.emit('leave', activeLobbyId.value, playerId.value);
}

function debugData() {
    socket.emit('debug_info')
}

socket.on('join_response', (data) => {
    if (data.status === 'success') {
        console.log("Join response success");
        activeLobbyId.value = data.lobby_id;
        $cookies.set('activeLobbyId', data.lobby_id, '1d');
        $cookies.set('playerId', playerId.value, '1d');
    }
    log(`${JSON.stringify(data)}`);
});

socket.on('leave_response', (data) => {
    if (data.status === 'success') {
        activeLobbyId.value = '';
        $cookies.remove('activeLobbyId');
        $cookies.remove('playerId');
    }
    log(`${JSON.stringify(data)}`);
});

socket.on('debug_info_data', (data) => {
    log(`${JSON.stringify(data)}`);
});

function attemptLoadCookie(varRef, cookieName: string) {
    const cookieValue = $cookies.get(cookieName);
    if (cookieValue) {
        varRef.value = cookieValue;
        log(`Loaded cookie value: ${cookieName} = ${cookieValue}`);
        return cookieValue;
    }
    return null;
}

onMounted(() => {
    attemptLoadCookie(activeLobbyId, 'activeLobbyId');
    attemptLoadCookie(playerId, 'playerId');
});

onBeforeUnmount(() => {
    leaveLobby();
    socket.disconnect();
});

</script>