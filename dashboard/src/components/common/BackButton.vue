<template>
	<Button variant="ghost" icon-left="chevron-left" :route="to" @click="$emit('click', $event)">
		{{ label }}
	</Button>
</template>

<script setup>
defineProps({
	to: {
		type: [String, Object],
		default: null,
	},
	label: {
		type: String,
		default: "Back",
	},
});

defineEmits(["click"]);
</script>
