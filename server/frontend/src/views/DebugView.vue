<script setup>
import { shallowRef } from 'vue';
import DebugNav from '@/components/debug/DebugNav.vue';
import DebugTools from '@/components/debug/DebugTools.vue';
import MapTools from '@/components/debug/MapTools.vue';

const componentMap = {
    DebugTools,
    MapTools
}

const activeComponent = shallowRef(DebugTools);

function handleNav(name) {
    if (componentMap[name]) {
        activeComponent.value = componentMap[name];
    }
}
</script>

<template>
    <DebugNav @debugNavigate="handleNav"/>
    <component :is="activeComponent"/>
</template>