# Design do Website

Este documento explica o design moderno e as escolhas de UI/UX implementadas.

## Características do Design

### 🎨 Visual Moderno

- **Gradientes suaves**: Uso de gradientes blue-to-indigo para elementos principais
- **Glassmorphism**: Efeito de vidro (backdrop-blur) nos cards
- **Sombras suaves**: Shadow-xl para profundidade
- **Bordas arredondadas**: Rounded-2xl para um look moderno
- **Animações sutis**: Transições suaves em hover e interações

### 🎯 UX/UI

- **Header fixo**: Header sticky com backdrop-blur para sempre acessível
- **Navegação por tabs**: Sistema de tabs elegante com gradiente
- **Feedback visual**: Estados de loading, success e error claros
- **Drag & Drop**: Área de upload com drag and drop
- **Responsivo**: Design que funciona em todos os tamanhos de tela

### 🎨 Paleta de Cores

- **Primária**: Blue-600 a Indigo-600 (gradientes)
- **Fundo**: Gradiente slate-50 → blue-50 → indigo-50
- **Cards**: Branco com opacidade (white/80) e backdrop-blur
- **Texto**: Gray-900 para texto principal, Gray-600 para secundário
- **Status**: 
  - Sucesso: Green-50/Green-200
  - Erro: Red-50/Red-200
  - Info: Blue-100/Blue-600

### 📐 Componentes

#### Header
- Sticky top com backdrop-blur
- Logo com gradiente text
- Indicador de status online

#### Tabs Navigation
- Botões com gradiente quando ativo
- Ícones SVG inline
- Transições suaves

#### Upload Component
- Área de drag & drop grande e clara
- Preview do arquivo selecionado
- Botão de upload com gradiente e hover effects
- Mensagens de sucesso/erro bem visíveis

#### Query Interface
- Textarea grande e confortável
- Resposta destacada em card
- Fontes numeradas e com scores
- Metadata colapsável

### ✨ Animações

- **fadeIn**: Entrada suave dos elementos
- **hover effects**: Transform e shadow nos botões
- **loading spinner**: Spinner animado durante carregamento
- **transitions**: Transições suaves em todas as interações

### 🎭 Detalhes de Design

1. **Ícones**: SVG inline para melhor performance
2. **Typography**: Font weights variados (bold para títulos, medium para labels)
3. **Spacing**: Espaçamento generoso (p-8, gap-4, space-y-6)
4. **Borders**: Bordas sutis com opacidade (border-gray-200/50)
5. **Scrollbar**: Customizada para melhor estética

## Tecnologias de Design

- **Tailwind CSS**: Utility-first CSS framework
- **CSS Gradients**: Para cores modernas
- **Backdrop Filter**: Para efeito glassmorphism
- **CSS Animations**: Para transições suaves
- **Flexbox/Grid**: Para layouts responsivos

## Responsividade

O design é totalmente responsivo usando:
- Container com max-width
- Padding adaptativo (px-4)
- Flexbox para layouts
- Texto que se ajusta automaticamente

## Acessibilidade

- Contrastes adequados (WCAG AA)
- Labels descritivos
- Estados focáveis visíveis
- Feedback claro para ações
- Texto legível (tamanhos adequados)

## Performance

- SVG inline (sem requests extras)
- Backdrop-filter (GPU accelerated)
- CSS puro (sem JavaScript para animações)
- Lazy loading de conteúdo (quando aplicável)
