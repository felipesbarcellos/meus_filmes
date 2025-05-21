<template>
  <div class="d-flex justify-content-center align-items-center mt-4 mt-md-5">
    <button
      class="btn btn-primary btn-sm me-2 me-md-3"
      :disabled="currentPage === 1 || loading"
      @click="changePage(currentPage - 1)"
    >
      <span class="d-none d-sm-inline">{{ $t('pagination.previous') }}</span>
      <span class="d-inline d-sm-none">&laquo;</span>
    </button>
    <span class="text-primary fw-bold mx-1">{{ $t('pagination.page') }} {{ currentPage }}</span>
    <button
      class="btn btn-primary btn-sm ms-2 ms-md-3"
      :disabled="!hasMorePages || loading"
      @click="changePage(currentPage + 1)"
    >
      <span class="d-none d-sm-inline">{{ $t('pagination.next') }}</span>
      <span class="d-inline d-sm-none">&raquo;</span>
    </button>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const props = defineProps({
  currentPage: {
    type: Number,
    required: true,
  },
  totalPages: { // Optional: if you know the total number of pages
    type: Number,
    default: 0,
  },
  hasMore: { // Used if totalPages is not available or for simpler logic
    type: Boolean,
    default: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['page-changed']);

const hasMorePages = computed(() => {
  if (props.totalPages > 0) {
    return props.currentPage < props.totalPages;
  }
  return props.hasMore;
});

function changePage(newPage) {
  if (newPage < 1) return;
  // If totalPages is known, don't go beyond it
  if (props.totalPages > 0 && newPage > props.totalPages && props.currentPage === props.totalPages) {
      // Already on the last page, and trying to go next (hasMorePages would be false)
      // This specific check might be redundant if :disabled relies correctly on hasMorePages
      return;
  }
  emit('page-changed', newPage);
}
</script>

<style scoped>
/* Styles for pagination controls if needed, otherwise rely on Bootstrap */
.btn:disabled {
  opacity: 0.65;
}
</style>
