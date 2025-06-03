<script setup lang="ts">
import { inject, onMounted, ref, watch } from 'vue';
import CombatGrid from '@/components/CombatGrid.vue';
import WorldView from '@/components/WorldView.vue';
import StatblockSelect from '@/components/StatblockSelect.vue';
import { VueCookies } from 'vue-cookies';
import { useRoute, useRouter } from 'vue-router';
import { io } from 'socket.io-client';

const viewMode = ref('CHARACTER_SELECT');
const viewData = ref(null);

const cookies = inject<VueCookies>('$cookies');
const route = useRoute();
const router = useRouter();
const campaignId = ref<string | null>(null);
const statblockId = ref<string | null>(null);
let socket;

const availableStatblocks = ref<{ id: string, name: string }[]>([]);

onMounted(() => {
    campaignId.value = route.query.cid as string || null;

    if (campaignId.value) {
        socket = io(import.meta.env.VITE_BACKEND_API_URL, {
            auth: {
                session_key: cookies.get('sessionKey') || null,
                campaign_id: campaignId.value
            }
        });

        socket.on('redirect', (data) => {
            console.log("Redirecting to:", data.url);
            if (data.url) {
                router.push(data.url);
            }
        });

        socket.on('command_response', (data) => {
            socket.emit('get_instance_data', {
                session_key: cookies.get('sessionKey') || null,
                campaign_id: campaignId.value,
                statblock_id: statblockId.value || null
            });
        });

        socket.on('disconnect', () => {
            router.push('/campaigns');
        });

        socket.on('connect_response', (response) => {
            console.log("Connected to server:", response);
            socket.emit('get_instance_data', {
                session_key: cookies.get('sessionKey') || null,
                campaign_id: campaignId.value,
                statblock_id: statblockId.value || null
            });
        });

        socket.on('set_instance_data', (d) => {
            // console.log("Received instance data:", d);
            viewMode.value = d.view;
            viewData.value = d.data;

            console.log("Set Instance Data:", viewData.value);
        });

        socket.on('error', (data) => {
            console.error("Socket Error:", data);
        });
    }
    else {
        router.push('/campaigns');
    }
});

function handleSetStatblockId(id: string) {
    statblockId.value = id;
    socket.emit('get_instance_data', {
        session_key: cookies.get('sessionKey') || null,
        campaign_id: campaignId.value,
        statblock_id: statblockId.value
    });
}

function sendCommand(playCommand) {
    socket.emit('send_command', {
        session_key: cookies.get('sessionKey') || null,
        campaign_id: campaignId.value,
        statblock_id: statblockId.value,
        command: playCommand.command,
        args: playCommand.args
    });
}

function setInstanceActType(actType: string) {
    socket.emit('set_instance_act_type', {
        session_key: cookies.get('sessionKey') || null,
        campaign_id: campaignId.value,
        statblock_id: statblockId.value,
        act_type: actType
    });
}
</script>

<template>
    <div class="flex w-screen h-screen">
        <div class="flex-grow h-full">
            <div v-if="statblockId" class="w-full h-full">
                <CombatGrid v-if="viewMode == 'COMBAT'" :data="viewData" @sendCommand="sendCommand" />
                <WorldView v-else-if="viewMode == 'WORLD'" :data="viewData" @sendCommand="sendCommand" />
            </div>
            <div class="w-full h-full" v-else>
                <StatblockSelect :data="viewData" @setStatblockId="handleSetStatblockId" />
            </div>
        </div>
        <div class="w-md max-w-md flex-shrink-0 h-full bg-gray-100">
            <p class="text-2xl">Sidebar</p>
            <button class="bg-blue-500 hover:bg-blue-700 active:bg-blue-900 text-white font-bold py-2 px-4 rounded m-2 cursor-pointer" @click="setInstanceActType('WORLD')">Set World Act</button>
            <button class="bg-green-500 hover:bg-green-700 active:bg-green-900 text-white font-bold py-2 px-4 rounded m-2 cursor-pointer" @click="setInstanceActType('COMBAT')">Set Combat Act</button>
        </div>
    </div>
</template>