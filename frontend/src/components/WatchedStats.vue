<template>
  <div class="d-flex align-items-start gap-4 mb-3">
    <WatchedCount :count="count" />
    <!-- Exemplo de uso futuro: estatísticas por gênero, etc. -->
    <!-- <div v-if="genres && genres.length > 0" class="text-light small">
      {{ $t('watchedStats.genres', { count: genres.length }) }}
    </div> -->
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import WatchedCount from './WatchedCount.vue'
const { t } = useI18n()
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
