// Utility para interceptar requisições HTTP e lidar com erros de token
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

// Armazenar a referência ao router quando for inicializado
let router

export function setupApi(appRouter) {
  router = appRouter
}

// Função para encapsular chamadas fetch com tratamento de erros de token
export async function apiCall(url, options = {}) {
  const authStore = useAuthStore()
  
  // Adicionar o token de autenticação se estiver disponível
  if (authStore.token) {
    options.headers = {
      ...options.headers,
      'Authorization': `Bearer ${authStore.token}`
    }
  }
  
  try {
    const response = await fetch(url, options)
    
    // Se a resposta for bem-sucedida, tenta retornar o JSON
    if (response.ok) {
      try {
        return await response.json()
      } catch (e) {
        return response
      }
    }

    // Se a resposta não for bem-sucedida, tenta obter os detalhes do erro
    let errorData
    try {
      errorData = await response.json()
    } catch (e) {
      errorData = { error: `HTTP Error: ${response.status}` }
    }

    // Se for erro 401, faz logout e redireciona para /login
    if (response.status === 401) {
      console.warn('Token inválido ou sessão expirada, redirecionando para login...')
      authStore.logout()
      if (router) {
        router.push('/login')
      }
      throw new Error('Sessão expirada')
    }
    
    // Para outros erros, propaga o erro recebido do servidor
    throw errorData
  } catch (error) {
    console.error('API call error:', error)
    throw error
  }
}

// Função wrapper para GET
export async function apiGet(url, options = {}) {
  return apiCall(url, { ...options, method: 'GET' })
}

// Função wrapper para POST
export async function apiPost(url, data, options = {}) {
  return apiCall(url, {
    ...options,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    body: JSON.stringify(data)
  })
}

// Função wrapper para PUT
export async function apiPut(url, data, options = {}) {
  return apiCall(url, {
    ...options,
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    body: JSON.stringify(data)
  })
}

// Função wrapper para DELETE
export async function apiDelete(url, options = {}) {
  return apiCall(url, { ...options, method: 'DELETE' })
}
