import { defineStore } from "pinia";
import { ref } from "vue";

export const useSearchStore = defineStore("search", () => {
  const searchQuery = ref("parkingLotName=");

  function setSearchQuery(query) {
    searchQuery.value = query;
  }

  return { searchQuery, setSearchQuery };
});
