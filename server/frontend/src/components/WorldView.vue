<template>
    <div class="flex flex-row justify-center items-center h-screen">
        <div class="flex flex-col">
            <p class="text-2xl mb-4 text-center">{{ locationName }}</p>
            <p class="text-lg mb-4 text-center">{{ locationDesc }}</p>
            <div class="flex flex-row">
                <button
                    v-for="location in adjacentLocations"
                    :key="location.id"
                    @click="emit('sendCommand', makePlayCommand('MOVE_LOCATION', [location.id]))"
                    class="bg-blue-500 hover:bg-blue-700 active:bg-blue-900 text-white font-bold py-2 px-4 rounded m-2 cursor-pointer"
                >
                    {{ location.name }}
                </button>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue';
import { makePlayCommand } from '@/composables/playCommand';

const locationName = ref('');
const locationDesc = ref('');
const adjacentLocations = ref<Array<{ id: string, name: string, desc: string }>>([]);

const props = defineProps({
    data: {
        type: Object,
        required: true
    }
});

const emit = defineEmits([
    'sendCommand',
    'refreshView'
]);

function handleCommandResponse(data) {
    emit('refreshView');
}

watch(() => props.data, (newData) => {
    locationName.value = newData.name;
    locationDesc.value = newData.description;
    adjacentLocations.value = newData.adjacent.map(element => {
        return { id: element[0], name: element[1] };
    });
}, { immediate: true });


defineExpose({
    handleCommandResponse
});
</script>