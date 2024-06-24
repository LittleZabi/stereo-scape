<script lang="ts">
	import Highcharts from 'highcharts';
	import { onMount } from 'svelte';
	// @ts-ignore
	import { getRandomChar } from '$lib/globals';
	export let seriesData: any = [];
	export let config: {
		width?: number;
		height?: number;
		xAxis?: boolean;
		yAxis?: boolean;
		title?: boolean | string;
		background?: string;
		line_color?: string | { linearGradient: number[]; stops: any[] };
	} = {};
	let setting = {
		line_color: {
			linearGradient: [0, 0, 400, 400],
			stops: [
				[0, '#ff3c60'],
				[0.3, '#00beff'],
				[0.6, '#00ff0e'],
				[0.9, '#fff900']
			]
		},
		width: 320,
		height: 200,
		xAxis: true,
		yAxis: true,
		title: true,
		background: '#172353b0',
		...config
	};
	let Chart = null;
	let element_id = 'id_' + getRandomChar(10);
	const updateChart = (series: any) => {
		if (Chart) Chart.series[0].update({ data: seriesData });
	};
	$: seriesData, updateChart(seriesData);
	onMount(() => {
		//@ts-ignore
		Chart = Highcharts.chart(element_id, {
			credits: {
				enabled: false
			},
			chart: {
				type: 'spline',
				backgroundColor: setting.background,
				height: setting.height,
				width: setting.width,
				style: {
					fontFamily: 'inherit',
					fontSize: '11px',
					borderRadius: '3px'
				}
			},
			plotBackgroundColor: null,
			title: setting.title
				? {
						text: 'PSNR (Peak Signal-to-Noise Ratio)',
						style: { color: 'white' }
					}
				: null,
			subtitle: null,

			xAxis: setting.xAxis
				? {
						lineWidth: 0,
						gridLineWidth: 0,
						minorGridLineWidth: 0,
						categories: seriesData.map((d: any) => d[0]),
						labels: {
							style: { color: 'white' },
							enabled: true,
							format: '{text}'
						}
					}
				: {
						text: null,
						gridLineWidth: 0,
						minorGridLineWidth: 0,
						tickWidth: 0,
						lineWidth: 0,
						labels: { enabled: false }
					},
			yAxis: setting.yAxis
				? {
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
					}
				: { title: { text: null }, gridLineWidth: 0, labels: { enabled: false } },
			tooltip: {
				formatter: function () {
					return (
						`<b>PSNR PER ITERATION</b><br>` +
						'iteration: ' +
						this.x +
						'<br>' +
						'psnr: ' +
						this.y.toFixed(4)
					);
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
					color: setting.line_color,
					data: seriesData.map((d) => d[1])
				}
			]
		});
	});
</script>

<div id={element_id} />
