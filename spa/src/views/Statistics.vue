<template>
    <section id="statistics" class="statistics">
        <h2 @mouseover="isMouseoverStatistics = true" @mouseout="isMouseoverStatistics = false">Statistics
        </h2>
        <el-button v-if="!isSort" :icon="SortDownRaw"
            @click="async () => { isSort = true; await pageUpdateForBarChart(true) }">
        </el-button>
        <el-button v-if="isSort" :icon="RefreshLeftRaw"
            @click="async () => { isSort = false; await pageUpdateForBarChart(true) }">
        </el-button>
        <div class="scroll-container" id="statistics-scroll-container" style="margin-top:15px;">
            <div>
                <div id="bar-chart" style="float: left; width: 100%; height: 500px;"></div>
            </div>
        </div>
    </section>
</template>

<script>
import * as echarts from 'echarts'
import { SortDown, RefreshLeft } from '@element-plus/icons-vue'
import { markRaw } from 'vue'

export default {
    components: { SortDown, RefreshLeft },
    data() {
        return {
            SortDownRaw: markRaw(SortDown),
            RefreshLeftRaw: markRaw(RefreshLeft),
            pxPerBar: 33,
            isSort: false,
            barChart: null,
            isBarClickAdded: false,
            isSortedBarClickAdded: false,
            isMouseoverStatistics: false,
            barChartDynamicSortZZTOption: {
                title: {
                    left: '3%',
                    top: '5%',
                    padding: ['10%', '10%', '10%', '10%'],
                    text: "",// support \n 
                },
                // tooltip: {
                //     trigger: 'axis'
                // },
                xAxis: {
                    max: "dataMax",
                    // boundaryGap: true,
                    lable: {
                        show: true,
                        position: "top"
                    }
                },
                yAxis: {
                    type: "category",
                    data: [],
                    inverse: true,
                    animationDuration: 300,
                    animationDurationUpdate: 300,
                    // max: 10, // only the largest max bars will be displayed

                    // boundaryGap: true,
                    axisTick: {
                        alignWithLabel: true
                    },
                },
                series: [
                    {
                        realtimeSort: this.isSort,
                        name: "Clip Statistics",
                        type: "bar",
                        data: [],
                        label: {
                            show: true,
                            position: "right",
                            distance: 10,
                            textStyle: {
                                color: "#D2CC13",
                                opacity: 0.7,
                            },
                            valueAnimation: true,
                        },
                        itemStyle: {
                            color: {
                                type: "linear",
                                x: 0, // right
                                y: 0, // down
                                x2: 1, // left
                                y2: 0, // up
                                colorStops: [
                                    {
                                        offset: 0,
                                        color: "rgb(32, 35, 41)"
                                    },
                                    {
                                        offset: 0.9,
                                        color: "#409EFF",
                                    },
                                ],
                            },
                        },
                    },
                ],
                legend: {
                    show: true,
                    textStyle: {
                        color: "#fff",
                        opacity: 0.7,
                    },
                },
                animationDuration: 3000,
                animationDurationUpdate: 3000,
                animationEasing: "linear",
                animationEasingUpdate: "linear"
            }
        }
    },
    props: {
        statistics: { type: Object, required: true },
        seekTo: { type: Function, required: true },
    },
    methods: {
        async handleBarClick(params) {
            await this.seekTo(this.statistics.timestamps[params.dataIndex])
        },

        async pageUpdateForBarChart(forceUpdate = false) {
            if (typeof this.statistics.seriesData === 'undefined') {
                return
            }
            // Check if the data has changed before updating the chart
            if (!forceUpdate && (JSON.stringify(this.barChartDynamicSortZZTOption.series[0].data) === JSON.stringify(this.statistics.seriesData) &&
                JSON.stringify(this.barChartDynamicSortZZTOption.yAxis.data) === JSON.stringify(this.statistics.yAxisData))
            ) {
                return
            }
            this.barChartDynamicSortZZTOption.series[0].data = this.statistics.seriesData
            this.barChartDynamicSortZZTOption.series[0].realtimeSort = this.isSort
            this.barChartDynamicSortZZTOption.title.text = "Total Time Watched: " + this.statistics.totalTime
            this.barChartDynamicSortZZTOption.yAxis.data = this.statistics.yAxisData
            const showLength = this.barChartDynamicSortZZTOption.yAxis.data.length
            var chartHeight = showLength * this.pxPerBar + 50
            if (chartHeight < 500) {
                chartHeight = 500;
            }
            const id = "bar-chart"
            var eleBarChart = document.getElementById(id)
            eleBarChart.style.height = String(chartHeight) + 'px'
            // if (this.barChart !== null) {
            //     this.barChart.dispose()
            // }
            this.barChart = echarts.init(eleBarChart)
            this.barChart.setOption(this.barChartDynamicSortZZTOption)
            if (!this.isSort && !this.isBarClickAdded) {
                this.isBarClickAdded = true
                this.barChart.on('click', async (params) => {
                    if (params.componentType === 'series') {
                        if (params.seriesType === 'bar') {
                            await this.handleBarClick(params)
                        }
                    }
                });
            }
            if (this.isSort && !this.isSortedBarClickAdded) {
                this.isSortedBarClickAdded = true
                this.barChart.on('click', async (params) => {
                    if (params.componentType === 'series') {
                        if (params.seriesType === 'bar') {
                            await this.handleBarClick(params)
                        }
                    }
                });
            }
        },
    },
    async mounted() {

        window.addEventListener("resize", () => {
            if (this.barChart !== null) {
                this.barChart.resize();
            }
        })

        setInterval(async () => {
            await this.pageUpdateForBarChart();
        }, 5000);
    },
    async beforeUnmount() {
        if (this.barChart !== null) {
            this.barChart.dispose()
        }
    }
}
</script>
