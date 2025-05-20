FROM node:23-alpine

WORKDIR /app

# Copia package.json e package-lock.json (se existir)
COPY package*.json ./

# Instala dependências
RUN npm install

# Copia o restante dos arquivos do frontend
COPY . .

# Constrói a aplicação para produção
RUN npm run build

# Instala um servidor estático simples
RUN npm install -g serve

EXPOSE 5173

# Serve a pasta 'dist' na porta 5173
CMD ["serve", "-s", "dist", "-l", "5173"]