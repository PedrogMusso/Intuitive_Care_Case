<template class="template">
  <div id="app-container">
    <div class="content-wrapper">
      <h1>Operadoras de Saúde</h1>
      <h2>Ordenadas por relevancia</h2>

      <!-- Listagem Principal -->
      <table v-if="operadoras.length > 0">
        <thead>
          <tr>
            <th>Registro ANS</th>
            <th>Nome Fantasia</th>
            <th>Razão Social</th>
            <th>Modalidade</th>
            <th>Relevância</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in operadoras" :key="item.Registro_ANS">
            <td>{{ item.Registro_ANS }}</td>
            <td>{{ item.Nome_Fantasia }}</td>
            <td>{{ item.Razao_Social }}</td>
            <td>{{ item.Modalidade }}</td>
            <td>{{ item.relevance.toFixed(1) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Paginação -->
      <div class="pagination" v-if="pagination.total_pages > 1">
        <button @click="changePage(page - 1)" :disabled="page === 1">Anterior</button>

        <span>Página {{ page }} de {{ pagination.total_pages }}</span>

        <button @click="changePage(page + 1)" :disabled="page === pagination.total_pages">
          Próxima
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'App',
  data() {
    return {
      operadoras: [],
      page: 1,
      pagination: {
        total_pages: 1,
      },
      loading: false,
    }
  },
  mounted() {
    this.loadOperadoras()
  },
  methods: {
    loadOperadoras() {
      this.loading = true
      axios
        .get(`http://localhost:5000/api/operadoras?page=${this.page}`)
        .then((response) => {
          this.operadoras = response.data.data
          this.pagination = response.data.pagination
        })
        .catch((error) => {
          console.error('Erro ao carregar operadoras:', error)
        })
        .finally(() => {
          this.loading = false
        })
    },
    changePage(newPage) {
      if (newPage > 0 && newPage <= this.pagination.total_pages) {
        this.page = newPage
        this.loadOperadoras()
      }
    },
  },
}
</script>

<style>
html,
body {
  display: block;
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
}

#app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100vw;
}

.content-wrapper {
  width: 90%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

h1,
h2 {
  text-align: center;
  margin: 10px 0;
}

.table-container {
  width: 100%;
  overflow-x: auto;
  margin: 20px 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 0 auto;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

th,
td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  font-weight: bold;
}

.pagination {
  margin: 30px 0;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
}

.pagination button {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.pagination button:hover:not(:disabled) {
  background-color: #f0f0f0;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination span {
  font-size: 0.9rem;
  color: #555;
}
</style>
