<template>
  <div class="d-flex align-items-center gap-2 mb-3">
    <span class="h3 text-primary mb-0 fw-bold">{{ count }}</span>
    <span class="text-light">filme{{ count === 1 ? '' : 's' }} assistido{{ count === 1 ? '' : 's' }}</span>
  </div>
</template>

<script setup>
const props = defineProps({
  count: {
    type: Number,
    required: true
  }
})
</script>

<style scoped>
/* All styling is now handled by Bootstrap classes */
</style>
