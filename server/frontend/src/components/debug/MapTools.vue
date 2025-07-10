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
</script>

<template>
    <div class="border-red-500 border-4 ml-auto mr-auto mt-6 w-3/4 h-9/12">
        <CombatGrid :data="mapData" @sendCommand="sendCommand" @refreshView="refreshInstanceView"/>
    </div>
</template>