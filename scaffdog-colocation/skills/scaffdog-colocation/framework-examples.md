# フレームワーク別 scaffdog テンプレート例

## React コンポーネント

`.scaffdog/react-component.md`:

```markdown
---
name: "react-component"
root: "src/components"
output: "**/*"
questions:
  name: "Component name (PascalCase):"
  withTest:
    confirm: "Include test file?"
    initial: true
  style:
    message: "Style solution:"
    choices:
      - "css-modules"
      - "tailwind"
      - "none"
  withStories:
    confirm: "Include Storybook stories?"
    initial: false
---

# `{{ inputs.name | pascal }}/index.ts`

\```ts
export { {{ inputs.name | pascal }} } from './{{ inputs.name | pascal }}';
export type { {{ inputs.name | pascal }}Props } from './{{ inputs.name | pascal }}.types';
\```

# `{{ inputs.name | pascal }}/{{ inputs.name | pascal }}.types.ts`

\```ts
export interface {{ inputs.name | pascal }}Props {
  children?: React.ReactNode;
  className?: string;
}
\```

# `{{ inputs.name | pascal }}/{{ inputs.name | pascal }}.tsx`

\```tsx
{{ if inputs.style == "css-modules" }}
import styles from './{{ inputs.name | pascal }}.module.css';
{{ end }}
import type { {{ inputs.name | pascal }}Props } from './{{ inputs.name | pascal }}.types';

export const {{ inputs.name | pascal }} = ({ children, className }: {{ inputs.name | pascal }}Props) => {
{{ if inputs.style == "css-modules" }}
  return <div className={styles.root}>{children}</div>;
{{ else if inputs.style == "tailwind" }}
  return <div className={className}>{children}</div>;
{{ else }}
  return <div>{children}</div>;
{{ end }}
};
\```

# `{{ inputs.name | pascal }}/{{ inputs.name | pascal }}.test.tsx`

{{ if inputs.withTest }}
\```tsx
import { render, screen } from '@testing-library/react';
import { {{ inputs.name | pascal }} } from './{{ inputs.name | pascal }}';

describe('{{ inputs.name | pascal }}', () => {
  it('renders children', () => {
    render(<{{ inputs.name | pascal }}>Hello</{{ inputs.name | pascal }}>);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
\```
{{ end }}

# `{{ inputs.name | pascal }}/{{ inputs.name | pascal }}.module.css`

{{ if inputs.style == "css-modules" }}
\```css
.root {
  /* {{ inputs.name | pascal }} styles */
}
\```
{{ end }}

# `{{ inputs.name | pascal }}/{{ inputs.name | pascal }}.stories.tsx`

{{ if inputs.withStories }}
\```tsx
import type { Meta, StoryObj } from '@storybook/react';
import { {{ inputs.name | pascal }} } from './{{ inputs.name | pascal }}';

const meta: Meta<typeof {{ inputs.name | pascal }}> = {
  title: 'Components/{{ inputs.name | pascal }}',
  component: {{ inputs.name | pascal }},
};

export default meta;
type Story = StoryObj<typeof {{ inputs.name | pascal }}>;

export const Default: Story = {
  args: {
    children: '{{ inputs.name | pascal }}',
  },
};
\```
{{ end }}
```

## React フック

`.scaffdog/react-hook.md`:

```markdown
---
name: "react-hook"
root: "src/hooks"
output: "**/*"
questions:
  name: "Hook name (without 'use' prefix):"
  withTest:
    confirm: "Include test file?"
    initial: true
---

# `use{{ inputs.name | pascal }}/index.ts`

\```ts
export { use{{ inputs.name | pascal }} } from './use{{ inputs.name | pascal }}';
\```

# `use{{ inputs.name | pascal }}/use{{ inputs.name | pascal }}.ts`

\```ts
import { useState, useCallback } from 'react';

export const use{{ inputs.name | pascal }} = () => {
  const [state, setState] = useState<unknown>(null);

  return { state };
};
\```

# `use{{ inputs.name | pascal }}/use{{ inputs.name | pascal }}.test.ts`

{{ if inputs.withTest }}
\```ts
import { renderHook } from '@testing-library/react';
import { use{{ inputs.name | pascal }} } from './use{{ inputs.name | pascal }}';

describe('use{{ inputs.name | pascal }}', () => {
  it('returns initial state', () => {
    const { result } = renderHook(() => use{{ inputs.name | pascal }}());
    expect(result.current.state).toBeNull();
  });
});
\```
{{ end }}
```

## Vue コンポーネント

`.scaffdog/vue-component.md`:

```markdown
---
name: "vue-component"
root: "src/components"
output: "**/*"
questions:
  name: "Component name (PascalCase):"
  withTest:
    confirm: "Include test file?"
    initial: true
  api:
    message: "API style:"
    choices:
      - "composition"
      - "options"
---

# `{{ inputs.name | pascal }}/index.ts`

\```ts
export { default as {{ inputs.name | pascal }} } from './{{ inputs.name | pascal }}.vue';
export type { {{ inputs.name | pascal }}Props } from './{{ inputs.name | pascal }}.types';
\```

# `{{ inputs.name | pascal }}/{{ inputs.name | pascal }}.types.ts`

\```ts
export interface {{ inputs.name | pascal }}Props {
  label?: string;
}
\```

# `{{ inputs.name | pascal }}/{{ inputs.name | pascal }}.vue`

{{ if inputs.api == "composition" }}
\```vue
<script setup lang="ts">
import type { {{ inputs.name | pascal }}Props } from './{{ inputs.name | pascal }}.types';

const props = withDefaults(defineProps<{{ inputs.name | pascal }}Props>(), {
  label: '{{ inputs.name | pascal }}',
});
</script>

<template>
  <div>{{ "{{" }} props.label {{ "}}" }}</div>
</template>

<style scoped>
/* {{ inputs.name | pascal }} styles */
</style>
\```
{{ else }}
\```vue
<script lang="ts">
import { defineComponent, type PropType } from 'vue';

export default defineComponent({
  name: '{{ inputs.name | pascal }}',
  props: {
    label: { type: String as PropType<string>, default: '{{ inputs.name | pascal }}' },
  },
});
</script>

<template>
  <div>{{ "{{" }} label {{ "}}" }}</div>
</template>
\```
{{ end }}

# `{{ inputs.name | pascal }}/{{ inputs.name | pascal }}.test.ts`

{{ if inputs.withTest }}
\```ts
import { mount } from '@vue/test-utils';
import {{ inputs.name | pascal }} from './{{ inputs.name | pascal }}.vue';

describe('{{ inputs.name | pascal }}', () => {
  it('renders label', () => {
    const wrapper = mount({{ inputs.name | pascal }}, {
      props: { label: 'Hello' },
    });
    expect(wrapper.text()).toContain('Hello');
  });
});
\```
{{ end }}
```

## Svelte コンポーネント

`.scaffdog/svelte-component.md`:

```markdown
---
name: "svelte-component"
root: "src/lib/components"
output: "**/*"
questions:
  name: "Component name (PascalCase):"
  withTest:
    confirm: "Include test file?"
    initial: true
---

# `{{ inputs.name | pascal }}/index.ts`

\```ts
export { default as {{ inputs.name | pascal }} } from './{{ inputs.name | pascal }}.svelte';
\```

# `{{ inputs.name | pascal }}/{{ inputs.name | pascal }}.svelte`

\```svelte
<script lang="ts">
  export let label: string = '{{ inputs.name | pascal }}';
</script>

<div class="{{ inputs.name | kebab }}">
  {label}
</div>

<style>
  .{{ inputs.name | kebab }} {
    /* {{ inputs.name | pascal }} styles */
  }
</style>
\```

# `{{ inputs.name | pascal }}/{{ inputs.name | pascal }}.test.ts`

{{ if inputs.withTest }}
\```ts
import { render, screen } from '@testing-library/svelte';
import {{ inputs.name | pascal }} from './{{ inputs.name | pascal }}.svelte';

describe('{{ inputs.name | pascal }}', () => {
  it('renders label', () => {
    render({{ inputs.name | pascal }}, { props: { label: 'Hello' } });
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
\```
{{ end }}
```

## TypeScript / Node.js モジュール

`.scaffdog/ts-module.md`:

```markdown
---
name: "ts-module"
root: "src"
output: "**/*"
questions:
  name: "Module name (kebab-case):"
  withTest:
    confirm: "Include test file?"
    initial: true
  withTypes:
    confirm: "Include types file?"
    initial: true
---

# `{{ inputs.name | kebab }}/index.ts`

\```ts
export { {{ inputs.name | camel }} } from './{{ inputs.name | kebab }}';
{{ if inputs.withTypes }}
export type { {{ inputs.name | pascal }}Options } from './{{ inputs.name | kebab }}.types';
{{ end }}
\```

# `{{ inputs.name | kebab }}/{{ inputs.name | kebab }}.ts`

\```ts
{{ if inputs.withTypes }}
import type { {{ inputs.name | pascal }}Options } from './{{ inputs.name | kebab }}.types';

export const {{ inputs.name | camel }} = (options?: {{ inputs.name | pascal }}Options) => {
  // Implementation
};
{{ else }}
export const {{ inputs.name | camel }} = () => {
  // Implementation
};
{{ end }}
\```

# `{{ inputs.name | kebab }}/{{ inputs.name | kebab }}.types.ts`

{{ if inputs.withTypes }}
\```ts
export interface {{ inputs.name | pascal }}Options {
  // Options
}

export interface {{ inputs.name | pascal }}Result {
  // Result
}
\```
{{ end }}

# `{{ inputs.name | kebab }}/{{ inputs.name | kebab }}.test.ts`

{{ if inputs.withTest }}
\```ts
import { {{ inputs.name | camel }} } from './{{ inputs.name | kebab }}';

describe('{{ inputs.name | camel }}', () => {
  it('works', () => {
    const result = {{ inputs.name | camel }}();
    expect(result).toBeDefined();
  });
});
\```
{{ end }}
```

## Feature モジュール

`.scaffdog/feature.md`:

```markdown
---
name: "feature"
root: "src/features"
output: "**/*"
questions:
  name: "Feature name (kebab-case):"
---

# `{{ inputs.name | kebab }}/index.ts`

\```ts
// Public API for {{ inputs.name | kebab }} feature
\```

# `{{ inputs.name | kebab }}/components/.gitkeep`

# `{{ inputs.name | kebab }}/hooks/.gitkeep`

# `{{ inputs.name | kebab }}/utils/.gitkeep`

# `{{ inputs.name | kebab }}/types/{{ inputs.name | kebab }}.types.ts`

\```ts
// Types for {{ inputs.name | kebab }} feature
\```

# `{{ inputs.name | kebab }}/constants/{{ inputs.name | kebab }}.constants.ts`

\```ts
// Constants for {{ inputs.name | kebab }} feature
\```
```
