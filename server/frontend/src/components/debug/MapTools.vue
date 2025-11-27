<script setup lang="ts">
import { reactive } from 'vue';
import CombatGrid from '../CombatGrid.vue';

const mapData = reactive({
    'map': {
        'width': 10,
        'height': 10,
        'max_height': 0,
        'tiles': [],
        'tokens': []
    },
    'hash': null
});

function sendCommand(playCommand) {
    
}

function refreshInstanceView() {

}

function updateWidth(event: Event) {
    const value = parseInt((event.target as HTMLInputElement).value);
    if (!isNaN(value) && value >= 1) {
        mapData.map.width = value;
    }
}

function updateHeight(event: Event) {
    const value = parseInt((event.target as HTMLInputElement).value);
    if (!isNaN(value) && value >= 1) {
        mapData.map.height = value;
    }
}
</script>

<template>
    <input id="grid-width" type="number" :value="mapData.map.width" @input="updateWidth" min="1"/>
    <input id="grid-height" type="number" :value="mapData.map.height" @input="updateHeight" min="1"/>
    <div class="border-blue-500 border-4 ml-auto mr-auto mt-6 w-3/4 h-9/12">
        <CombatGrid :data="mapData" @sendCommand="sendCommand" @refreshView="refreshInstanceView"/>
    </div>
</template>