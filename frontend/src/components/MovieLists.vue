<script setup>
import { ref, onMounted, watch } from 'vue' // Adicionado watch
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth' // Importar o store Pinia
import { apiGet, apiPost, apiPut, apiDelete } from '@/utils/api'

const lists = ref([])
const loading = ref(true)
const error = ref('')

const router = useRouter()
const authStore = useAuthStore() // Usar o store Pinia

const { t } = useI18n()

const BACKEND_API_URL = '/api'

async function fetchLists() {
    if (!authStore.isAuthenticated || !authStore.user?.id) {
        lists.value = []
        loading.value = false
        return
    }
    loading.value = true
    error.value = ''
    try {
        // Usa apiGet para garantir tratamento centralizado de token
        const data = await apiGet(`${BACKEND_API_URL}/lists/`)
        lists.value = data
    } catch (e) {
        error.value = e.message || 'Erro ao buscar listas'
        lists.value = [] // Limpa as listas em caso de erro para evitar mostrar dados antigos
    } finally {
        loading.value = false
    }
}

async function createList() {
  if (!authStore.isAuthenticated || !authStore.user?.id) {
    alert(t('movieLists.errors.authRequired'))
    return
  }
  const name = prompt(t('movieLists.prompts.newListName'))
  if (!name || !name.trim()) return

  loading.value = true
  try {
    await apiPost(`${BACKEND_API_URL}/lists/`, { name })
    await fetchLists() // Recarrega as listas após a criação
  } catch (e) {
    error.value = e.message || 'Erro ao criar lista'
  } finally {
    loading.value = false
  }
}

async function deleteList(listId) {
  if (!authStore.isAuthenticated) {
    alert(t('movieLists.errors.authRequired'))
    return
  }
  if (!confirm(t('movieLists.prompts.confirmDelete'))) return

  loading.value = true
  try {
    await apiDelete(`${BACKEND_API_URL}/lists/${listId}`)
    await fetchLists() // Recarrega as listas após a exclusão
  } catch (e) {
    error.value = e.message || 'Erro ao excluir lista'
  } finally {
    loading.value = false
  }
}

async function editListName(list) {
  if (!authStore.isAuthenticated) {
    alert(t('movieLists.errors.authRequired'))
    return
  }
  const newName = prompt(t('movieLists.prompts.editListName'), list.name)
  if (!newName || !newName.trim() || newName === list.name) return

  loading.value = true
  try {
    await apiPut(`${BACKEND_API_URL}/lists/${list.id}`, { name: newName })
    await fetchLists() // Recarrega as listas após a edição
  } catch (e) {
    error.value = e.message || 'Erro ao atualizar nome da lista'
  } finally {
    loading.value = false
  }
}

function goToList(list) {
  // Garante que o id é primitivo (string ou number)
  const id = typeof list === 'object' && list !== null && 'id' in list ? list.id : list
  if (id !== undefined && id !== null && id !== '') {
    router.push(`/listas/${id}`)
  } else {
    console.warn('ID de lista inválido ao tentar navegar:', id)
  }
}

// Observa o estado de autenticação para buscar/limpar listas
watch(() => authStore.isAuthenticated, (newIsAuthenticated) => {
  if (newIsAuthenticated) {
    fetchLists()
  } else {
    lists.value = [] // Limpa as listas se o usuário deslogar
    error.value = ''; // Limpa erros anteriores
  }
}, { immediate: true }) // `immediate: true` para rodar na montagem inicial

</script>

<template>
  <div class="card bg-dark text-light shadow-lg mx-auto mt-4 mb-5" style="max-width: 650px;">
    <div class="card-body p-4">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="h3 mb-0">{{ $t('movieLists.title') }}</h2>
        <button class="btn btn-primary" @click="createList">
          <i class="bi bi-plus-circle me-1"></i> {{ $t('movieLists.newListButton') }}
        </button>
      </div>
      
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">{{ $t('movieLists.loading.srOnly') }}</span>
        </div>
        <p class="mt-2 text-secondary">{{ $t('movieLists.loading.text') }}</p>
      </div>
      
      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>
      
      <div v-else-if="lists.length === 0" class="alert alert-secondary text-center py-3">
        {{ $t('movieLists.noLists') }}
      </div>
      
      <ul v-else class="list-group list-group-flush">
        <li v-for="list in lists" 
            :key="list.id" 
            class="list-group-item bg-dark border-secondary d-flex justify-content-between align-items-center mb-2 rounded"
            @click="goToList(list)">
          <div class="d-flex align-items-center">
            {{ list.name }}
            <span v-if="list.is_main" class="badge bg-primary ms-2">{{ $t('movieLists.defaultBadge') }}</span>
          </div>
          
          <div class="btn-group">
            <button class="btn btn-sm btn-outline-primary" 
                    :title="$t('movieLists.actions.editTitle')" 
                    @click.stop="editListName(list)">
              ✏️
            </button>
            <button class="btn btn-sm btn-outline-danger" 
                    :title="$t('movieLists.actions.deleteTitle')" 
                    @click.stop="deleteList(list.id)">
              🗑️
            </button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
/* Custom pointer cursor for list items */
.list-group-item {
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.list-group-item:hover {
  background-color: var(--bs-gray-800) !important;
}

/* Keep button hover states separate from list item hover */
.btn-outline-primary:hover, .btn-outline-danger:hover {
  z-index: 1;
}
</style>