<script setup>
  import Navbar from './components/Navbar.vue';
  import { useRoute } from 'vue-router';
  import { computed } from 'vue';

  const route = useRoute();

  const isAuthRoute = computed(() => route.path == '/login' || route.path == '/register')
</script>

<template>
  <header>
    <Navbar v-if="!isAuthRoute" />
    <RouterView />
  </header>
</template>
