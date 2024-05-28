<script lang="ts">
	import Highcharts from 'highcharts';
	import { onMount } from 'svelte';
	export let seriesData: any = [];
	console.log(seriesData);
	let Chart = null;
	const updateChart = (series: any) => {
		if (Chart) Chart.series[0].update({ data: seriesData });
	};
	$: seriesData, updateChart(seriesData)
		onMount(() => {
			//@ts-ignore
			Chart = Highcharts.chart('chart', {
				credits: {
					enabled: false
				},
				chart: {
					type: 'spline',
					backgroundColor: '#172353b0',
					height: 200,
					width: 320,
					style: {
						fontFamily: 'inherit',
						fontSize: '11px',
						borderRadius: '3px'
					}
				},
				plotBackgroundColor: null,
				title: {
					text: 'PSNR (Peak Signal-to-Noise Ratio)',
					style: { color: 'white' }
				},
				subtitle: null,

				xAxis: {
					lineWidth: 0,
					gridLineWidth: 0,
					minorGridLineWidth: 0,
					categories: seriesData.map((d: any) => d[0]),
					labels: {
						style: { color: 'white' },
						enabled: true,
						format: '{text}'
					}
				},
				yAxis: {
					categories: seriesData.map((d) => d[1].toFixed(1)),
					gridLineWidth: 0.2,
					labels: {
						style: { color: 'white' },
						enabled: true,
						format: '{text} dB'
					},
					title: {
						text: null
					}
				},
				tooltip: {
					formatter: function () {
						return this.x;
					}
				},
				plotOptions: {
					spline: {
						dataLabels: {
							enabled: false
						},
						marker: {
							enabled: false
						}
					}
				},
				legend: {
					enabled: false
				},
				series: [
					{
						name: null,
						color: {
							linearGradient: [0, 0, 400, 400],
							stops: [
								[0, '#ff3c60'],
								[0.3, '#00beff'],
								[0.6, '#00ff0e'],
								[0.9, '#fff900']
							]
						},
						data: seriesData.map((d) => d[1])
					}
				]
			});
		});
</script>

<div id="chart" />
