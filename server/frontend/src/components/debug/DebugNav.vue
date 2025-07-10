<script setup>
const emit = defineEmits([
    'debugNavigate'
]);

const debugComponentButtons = {
    'DebugTools': 'Debug Tools',
    'MapTools': 'Room Layouts'
}

const debugNavigate = (componentName) => {
    emit('debugNavigate', componentName);
};
</script>

<template>
    <div class="sticky top-0 w-full bg-white shadow-md p-2 z-10 flex flex-row justify-center">
        <button
            v-for="(label, name) in debugComponentButtons"
            :key="name"
            @click="debugNavigate(name)"
            class="bg-blue-500 hover:bg-blue-700 active:bg-blue-900 text-white font-bold py-2 px-4 rounded m-2 cursor-pointer"
        >
            {{ label }}
        </button>
    </div>
</template>