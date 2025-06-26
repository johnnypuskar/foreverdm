<template>
    <div class="flex flex-row justify-center items-center h-screen">
        <div class="flex flex-col">
            <p class="text-2xl mb-4 text-center">Select Character</p>
            <button
                v-for="statblock in statblocks"
                :key="statblock.id"
                @click="emit('setStatblockId', statblock.id)"
                class="bg-blue-500 hover:bg-blue-700 active:bg-blue-900 text-white font-bold py-2 px-4 rounded m-2 cursor-pointer"
            >
                {{ statblock.name }}
            </button>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue';

const statblocks = ref([])

const props = defineProps({
    data: {
        type: Object,
        required: true
    }
});
const emit = defineEmits([
    'setStatblockId'
]);

watch(() => props.data, (newData) => {
    statblocks.value = newData.map(element => {
        return { id: element[0], name: element[1] };
    });
});

</script>