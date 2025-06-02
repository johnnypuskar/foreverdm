<template>
    <div class="flex flex-row justify-center items-center h-screen">
        <div class="flex flex-col">
            <p class="text-2xl mb-4 text-center">Debug Tools</p>
            <p class="text-md mb-4 text-center">{{ lastResponseMessage }}</p>
            <div class="border-b-gray-400 border-b-2 mb-4">
                <span class="text-lg mb-2">Global Debug Parameters</span>
                <input type="text" v-model="campaignId" placeholder="Campaign ID" class="border border-gray-300 rounded p-2 m-2">
                <input type="text" v-model="locationId" placeholder="Location ID" class="border border-gray-300 rounded p-2 m-2">
                <button @click="addCampaign" class="bg-blue-500 hover:bg-blue-700 active:bg-blue-900 text-white font-bold py-2 px-4 rounded m-2 cursor-pointer">
                    Add Campaign
                </button>
                <button @click="joinCampaign" class="bg-green-500 hover:bg-green-700 active:bg-green-900 text-white font-bold py-2 px-4 rounded m-2 cursor-pointer">
                    Join Campaign
                </button>
            </div>

            <div>
                <span class="text-lg mb-2">Add Statblock</span>
                <input type="text" v-model="statblockId" placeholder="Statblock ID" class="border border-gray-300 rounded p-2 m-2">
                <input type="text" v-model="statblockName" placeholder="Statblock Name" class="border border-gray-300 rounded p-2 m-2">
                <button @click="addStatblock" class="bg-blue-500 hover:bg-blue-700 active:bg-blue-900 text-white font-bold py-2 px-4 rounded m-2 cursor-pointer">
                    Add Statblock
                </button>
            </div>
            
            <div>
                <span class="text-lg mb-2">Add Location</span>
                <input type="text" v-model="locationName" placeholder="Location Name" class="border border-gray-300 rounded p-2 m-2">
                <input type="text" v-model="locationDesc" placeholder="Location Description" class="border border-gray-300 rounded p-2 m-2">
                <button @click="addLocation" class="bg-blue-500 hover:bg-blue-700 active:bg-blue-900 text-white font-bold py-2 px-4 rounded m-2 cursor-pointer">
                    Add Location
                </button>
            </div>

            <div>
                <span class="text-lg mb-2">Make Locations Adjacent</span>
                <input type="text" v-model="secondaryLocationID" placeholder="Second Location ID" class="border border-gray-300 rounded p-2 m-2">
                <button @click="makeLocationsAdjacent" class="bg-blue-500 hover:bg-blue-700 active:bg-blue-900 text-white font-bold py-2 px-4 rounded m-2 cursor-pointer">
                    Make Adjacent
                </button>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { inject, ref } from 'vue';
import { VueCookies } from 'vue-cookies';

const cookies = inject<VueCookies>('$cookies');

const lastResponseMessage = ref('--');

const campaignId = ref('');
const locationId = ref('');

const statblockId = ref('');
const statblockName = ref('');

const locationName = ref('');
const locationDesc = ref('');

const secondaryLocationID = ref('');

async function addStatblock() {
    lastResponseMessage.value = '--';
    const url = `${import.meta.env.VITE_BACKEND_API_URL}/admin/add-statblock`;
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_key: cookies.get('sessionKey'),
            campaign_id: campaignId.value,
            location_id: locationId.value,
            statblock_id: statblockId.value,
            statblock_name: statblockName.value,
            statblock_data: {name: statblockName.value, id: statblockId.value}
        })
    });
    const responseData = await response.json();
    lastResponseMessage.value = responseData.message;
}

async function addLocation() {
    lastResponseMessage.value = '--';
    const url = `${import.meta.env.VITE_BACKEND_API_URL}/admin/add-location`;
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            campaign_id: campaignId.value,
            location_id: locationId.value,
            location_name: locationName.value,
            location_desc: locationDesc.value
        })
    });
    const responseData = await response.json();
    lastResponseMessage.value = responseData.message;
}

async function makeLocationsAdjacent() {
    lastResponseMessage.value = '--';
    const url = `${import.meta.env.VITE_BACKEND_API_URL}/admin/add-adjacency`;
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            campaign_id: campaignId.value,
            first_location_id: locationId.value,
            second_location_id: secondaryLocationID.value
        })
    });
    const responseData = await response.json();
    lastResponseMessage.value = responseData.message;
}

async function addCampaign() {
    lastResponseMessage.value = '--';
    const url = `${import.meta.env.VITE_BACKEND_API_URL}/admin/add-campaign`;
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            campaign_id: campaignId.value
        })
    });
    const responseData = await response.json();
    lastResponseMessage.value = responseData.message;
}

async function joinCampaign() {
    lastResponseMessage.value = '--';
    const url = `${import.meta.env.VITE_BACKEND_API_URL}/admin/join-campaign`;
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_key: cookies.get('sessionKey'),
            campaign_id: campaignId.value
        })
    });
    const responseData = await response.json();
    lastResponseMessage.value = responseData.message;
}
</script>