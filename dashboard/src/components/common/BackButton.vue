<template>
	<Button variant="ghost" icon-left="chevron-left" :route="to" @click="$emit('click', $event)">
		{{ label }}
	</Button>
</template>

<script setup lang="ts">
import type { RouteLocationRaw } from "vue-router";

interface Props {
	to?: RouteLocationRaw | null;
	label?: string;
}

withDefaults(defineProps<Props>(), {
	to: null,
	label: "Back",
});

defineEmits<{
	(e: "click", event: MouseEvent): void;
}>();
</script>
