<template>
    <div class="flex flex-row justify-center mt-6 h-screen">
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

            <div>
                <div>
                    <span class="text-lg mb-2">Precompute Region Configurations</span>
                    <button @click="precomputeConfigurations" class="bg-green-500 hover:bg-green-700 active:bg-green-900 text-white font-bold py-2 px-4 rounded m-2 cursor-pointer">
                        Precompute Configurations
                    </button>
                </div>
                <div>
                    <span class="text-sm inline-block w-42">Length (min/max):</span>
                    <input type="number" min="1" max="12" v-model="regionsLength.min" class="border rounded px-2 py-1 w-20 ml-2">
                    <input type="number" min="1" max="12" v-model="regionsLength.max" class="border rounded px-2 py-1 w-20 ml-1">
                </div>
                <div class="mt-2">
                    <span class="text-sm inline-block w-42">Width (min/max):</span>
                    <input type="number" min="1" max="12" v-model="regionsWidth.min" class="border rounded px-2 py-1 w-20 ml-2">
                    <input type="number" min="1" max="12" v-model="regionsWidth.max" class="border rounded px-2 py-1 w-20 ml-1">
                </div>
                <div class="mt-2">
                    <span class="text-sm inline-block w-42">Back T Length (min/max):</span>
                    <input type="number" min="0" max="12" v-model="regionsBackTHeight.min" class="border rounded px-2 py-1 w-20 ml-2">
                    <input type="number" min="0" max="12" v-model="regionsBackTHeight.max" class="border rounded px-2 py-1 w-20 ml-1">
                </div>
                <div class="mt-2">
                    <span class="text-sm inline-block w-42">Back T Width (min/max):</span>
                    <input type="number" min="0" max="12" v-model="regionsBackTWidth.min" class="border rounded px-2 py-1 w-20 ml-2">
                    <input type="number" min="0" max="12" v-model="regionsBackTWidth.max" class="border rounded px-2 py-1 w-20 ml-1">
                </div>
                <div class="mt-2">
                    <span class="text-sm inline-block w-42">Back T Offset (min/max):</span>
                    <input type="number" min="0" max="12" v-model="regionsBackTOffset.min" class="border rounded px-2 py-1 w-20 ml-2">
                    <input type="number" min="0" max="12" v-model="regionsBackTOffset.max" class="border rounded px-2 py-1 w-20 ml-1">
                </div>
                <div class="mt-2">
                    <span class="text-sm inline-block w-42">Front T Length (min/max):</span>
                    <input type="number" min="0" max="12" v-model="regionsFrontTHeight.min" class="border rounded px-2 py-1 w-20 ml-2">
                    <input type="number" min="0" max="12" v-model="regionsFrontTHeight.max" class="border rounded px-2 py-1 w-20 ml-1">
                </div>
                <div class="mt-2">
                    <span class="text-sm inline-block w-42">Front T Width (min/max):</span>
                    <input type="number" min="0" max="12" v-model="regionsFrontTWidth.min" class="border rounded px-2 py-1 w-20 ml-2">
                    <input type="number" min="0" max="12" v-model="regionsFrontTWidth.max" class="border rounded px-2 py-1 w-20 ml-1">
                </div>
                <div class="mt-2">
                    <span class="text-sm inline-block w-42">Front T Offset (min/max):</span>
                    <input type="number" min="0" max="12" v-model="regionsFrontTOffset.min" class="border rounded px-2 py-1 w-20 ml-2">
                    <input type="number" min="0" max="12" v-model="regionsFrontTOffset.max" class="border rounded px-2 py-1 w-20 ml-1">
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { inject, reactive, ref } from 'vue';
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

const regionsLength = reactive({ min: 1, max: 1 })
const regionsWidth = reactive({ min: 1, max: 1 });
const regionsBackTWidth = reactive({ min: 0, max: 0 });
const regionsBackTHeight = reactive({ min: 0, max: 0 }); 
const regionsBackTOffset = reactive({ min: 0, max: 0 });
const regionsFrontTWidth = reactive({ min: 0, max: 0 });
const regionsFrontTHeight = reactive({ min: 0, max: 0 });
const regionsFrontTOffset = reactive({ min: 0, max: 0 });

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

async function precomputeConfigurations() {
    lastResponseMessage.value = 'Precomputing configurations...';
    const url = `${import.meta.env.VITE_BACKEND_API_URL}/admin/precompute-room-configs`;
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            min_length: regionsLength.min,
            max_length: regionsLength.max,
            min_width: regionsWidth.min,
            max_width: regionsWidth.max,
            min_back_t_length: regionsBackTHeight.min,
            max_back_t_length: regionsBackTHeight.max,
            min_back_t_width: regionsBackTWidth.min,
            max_back_t_width: regionsBackTWidth.max,
            min_back_t_offset: regionsBackTOffset.min,
            max_back_t_offset: regionsBackTOffset.max,
            min_front_t_length: regionsFrontTHeight.min,
            max_front_t_length: regionsFrontTHeight.max,
            min_front_t_width: regionsFrontTWidth.min,
            max_front_t_width: regionsFrontTWidth.max,
            min_front_t_offset: regionsFrontTOffset.min,
            max_front_t_offset: regionsFrontTOffset.max
        })
    });
    const responseData = await response.json();
    lastResponseMessage.value = responseData.message || `Status: ${response.status}`;
}
</script>