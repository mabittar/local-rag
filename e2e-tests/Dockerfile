FROM mcr.microsoft.com/playwright:v1.49.0-focal

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install

# Copy tests
COPY . .

# Playwright requires some system dependencies already in the image, 
# but let's ensure we can run it
CMD ["pnpm", "run", "test"]
