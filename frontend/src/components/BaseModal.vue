<template>
  <div v-if="show" class="modal-backdrop-container">
    <!-- Modal backdrop -->
    <div class="modal-backdrop fade show"></div>

    <!-- Modal wrapper (centers content) -->
    <div
      class="modal fade show d-block modal-outer-wrapper"
      tabindex="-1"
      @click.self="emit('close')"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <!-- Header -->
          <div class="modal-header">
            <h5 class="modal-title">{{ title }}</h5>
            <button
              type="button"
              class="btn-close"
              @click="emit('close')"
            ></button>
          </div>

          <form @submit.prevent="emit('submit')">
            <!-- Body -->
            <div class="modal-body">
              <slot name="body"></slot>
            </div>

            <!-- Footer (customizable) -->
            <div class="modal-footer">
              <slot name="footer">
              </slot>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  show: Boolean,
  title: { type: String, default: "Modal Title" },
});

const emit = defineEmits(["close", "submit"]);
</script>

<style scoped>
.modal-backdrop-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1050;
}

.modal-outer-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}
</style>
