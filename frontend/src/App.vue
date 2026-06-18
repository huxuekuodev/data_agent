<template>
  <div id="app">
    <LoginModal v-if="!isAuthenticated" />
    <ChatInterface v-else />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import LoginModal from '@/components/LoginModal.vue'
import ChatInterface from '@/components/ChatInterface.vue'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
</script>

<style scoped>
#app {
  width: 100%;
  height: 100vh;
}
</style>