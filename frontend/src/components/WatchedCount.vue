<template>
  <div class="d-flex align-items-center gap-2 mb-3">
    <span class="h3 text-primary mb-0 fw-bold">{{ count }}</span>
    <span class="text-light">
      {{ $tc('watchedCount.label', count, { count }) }}
    </span>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t, tc } = useI18n()
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
