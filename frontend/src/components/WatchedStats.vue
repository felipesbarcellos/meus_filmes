<template>
  <div class="d-flex align-items-start gap-4 mb-3">
    <WatchedCount :count="count" />
  </div>
</template>

<script setup>
import WatchedCount from './WatchedCount.vue'
const props = defineProps({
  count: {
    type: Number,
    required: true
  },
  movies: {
    type: Array,
    required: true
  },
  genres: {
    type: Array,
    required: true
  }
})
</script>

<style scoped>
/* All styling is now handled by Bootstrap classes */
</style>
