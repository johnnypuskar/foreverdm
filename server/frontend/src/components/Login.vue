<script setup lang="ts">
import { inject } from 'vue';
import { VueCookies } from 'vue-cookies';

const cookies = inject<VueCookies>('$cookies');

const googleCallback = async (response) => {
    const loginResponse = await fetch(`${import.meta.env.VITE_BACKEND_API_URL}/auth/google`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            credential: response.credential,
        })
    });
    if (loginResponse.ok) {
        const data = await loginResponse.json();
        console.log("Login response:", data);
        if (data.status === 'success') {
            cookies.set('sessionKey', data.session_key, '1d');
        }
    }
}
</script>

<template>
    <GoogleLogin :callback="googleCallback"/>
</template>