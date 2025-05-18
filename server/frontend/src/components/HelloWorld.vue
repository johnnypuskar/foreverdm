<template>
    <div class="text-red-500">
        Hello, world!
    </div>
    <div>
        <form @submit.prevent="sendMessage">
            <input type="text" v-model="messageText" placeholder="Enter message" />
            <button type="submit">Send</button>
        </form>
    </div>
    <button @click="ping">
        Ping
    </button>

</template>

<script setup>
import { ref, onMounted, onUnmounted, onBeforeUnmount } from 'vue';
import { io } from 'socket.io-client';

const socket = io('http://localhost:5000');

const messageText = ref('');

function sendMessage() {
    if (messageText.value.trim() === '') return;
    console.log('Sending message:', messageText.value);
    socket.emit('message', messageText.value);
    messageText.value = '';
}

function ping() {
    console.log('Ping button clicked');
    socket.emit('ping');
}

onBeforeUnmount(() => {
    socket.disconnect();
});

</script>