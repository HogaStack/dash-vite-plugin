<template>
  <div id="vue-app">
    <h1>{{ message }}</h1>
    <div>
      <button id="control-dash-button" @click="updateDash">Control Dash</button>
    </div>
    <div hidden>
      <button id="control-vue-button" @click="updateMessage">
        Control Vue
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

const message = ref("Hello from Vue!");

const updateDash = () => {
  message.value = "Hello from Vue!";
  window.dash_clientside.set_props("dash-title", {
    children: "Hello from Vue!",
  });
};

const updateMessage = () => {
  message.value = "Hello from Dash!";
};
</script>

<style scoped>
#vue-app {
  margin: 20px;
}
h1 {
  color: #42b883;
}
</style>
