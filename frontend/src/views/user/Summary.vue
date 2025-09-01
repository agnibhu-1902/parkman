<script setup>
import { onMounted, ref } from "vue";
import axios from "../../config/api";
import BarChart from "../../components/BarChart.vue";
import PieChart from "../../components/PieChart.vue";

const barChartData = ref({
  location: [],
  datasets: [],
});
const pieChartData = ref({
  location: [],
  datasets: [],
});
const barChartOptions = ref({
  responsive: true,
  indexAxis: "y",
  maintainAspectRatio: false,
  plugins: {
    legend: { position: "top" },
    title: {
      display: true,
      text: "Parking Lot Visits",
      font: {
        size: 20,
        weight: "bold",
      },
      color: "black",
      padding: {
        top: 10,
        bottom: 20,
      },
    },
  },
  scales: {
    x: {
      title: {
        display: true,
        text: "Times visited",
      },
      min: 0,
      ticks: {
        stepSize: 1,
      },
    },
  },
});
const pieChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: "top" },
    title: {
      display: true,
      text: "Parking Lot Expenses",
      font: {
        size: 20,
        weight: "bold",
      },
      color: "black",
      padding: {
        top: 10,
        bottom: 20,
      },
    },
  },
});

onMounted(async () => {
  const response = await axios.get("/api/parking-lots/summary");

  if (!response.status == 200 || !response.data.success) return;

  const lots = response.data.lots;
  const labels = lots.map((lot) => lot.location);
  const visitCounts = lots.map((lot) => lot.total_visits);
  const spendings = lots.map((lot) => lot.total_spent);

  barChartData.value = {
    labels,
    datasets: [
      {
        label: "Total Visits",
        data: visitCounts,
        backgroundColor: "#FF6384",
      },
    ],
  };

  pieChartData.value = {
    labels,
    datasets: [
      {
        label: "Total Spent",
        data: spendings,
        backgroundColor: [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#8AFFC1",
          "#FFA07A",
        ],
      },
    ],
  };
});
</script>

<template>
  <div class="vh-100" style="padding-top: 70px">
    <div class="container">
      <div v-if="barChartData.datasets.length || pieChartData.datasets.length">
        <h1 class="text-center mb-4">Summary</h1>
        <div class="row">
          <div class="col-md-6" style="height: 70vh">
            <PieChart :chart-data="pieChartData" :options="pieChartOptions" />
          </div>
          <div class="col-md-6" style="height: 70vh">
            <BarChart :chart-data="barChartData" :options="barChartOptions" />
          </div>
        </div>
      </div>
      <div
        v-if="!barChartData.datasets.length && !pieChartData.datasets.length"
        class="text-center w-100 h-100 overflow-hidden"
      >
        <h1 class="text-center mb-4">Summary</h1>
        <img
          src="/images/sad_ghost.png"
          alt="No data found"
          style="width: 200px; height: 150px"
        />
        <p class="fs-3 text-muted">Nothing to show here</p>
      </div>
    </div>
  </div>
</template>
