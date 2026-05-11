from typing import Iterable, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import pandas as pd


# Helper functions for plotting solution results and sensitivity analyses

# Assumes solution_df has columns: 'route', 'time_block', 'n_old', 'n_new', 'delta_n'
def sort_route_index(index_vals):
    return sorted(index_vals, key=lambda x: int(x) if str(x).isdigit() else str(x))

def make_plot_labels(time_block='all', value_col='n_new'):
    block_label = 'all time blocks' if time_block == 'all' else time_block
    y_label = {
        'n_new': 'Bus allocation (n_new)',
        'delta_n': 'Bus change from baseline (delta_n)',
    }[value_col]
    return block_label, y_label

# Aggregation and plotting helper functions
def aggregate_single_solution(solution_df, time_block='all', value_col='n_new'):
    if value_col not in ['n_new', 'delta_n']:
        raise ValueError("value_col must be 'n_new' or 'delta_n'")

    df_plot = solution_df.copy()
    if time_block != 'all':
        if time_block not in df_plot['time_block'].unique():
            raise ValueError(f'Unknown time_block: {time_block}')
        df_plot = df_plot[df_plot['time_block'] == time_block].copy()

    grouped = df_plot.groupby('route', as_index=False)[['n_old', 'n_new', 'delta_n']].sum()
    grouped['plot_value'] = grouped[value_col]
    return grouped

# For sensitivity analysis, need to aggregate by both route and parameter value
def make_plot_frame(solution_df, time_block='all', value_col='n_new', route_filter=None, sort_routes_numeric=True):
    grouped = aggregate_single_solution(solution_df=solution_df, time_block=time_block, value_col=value_col)

    if route_filter is not None:
        grouped = grouped[grouped['route'].isin(route_filter)].copy()
        target_index = list(route_filter)
    elif sort_routes_numeric:
        target_index = sort_route_index(grouped['route'].tolist())
    else:
        target_index = grouped['route'].tolist()

    grouped = grouped.set_index('route').reindex(target_index).reset_index()
    grouped['plot_value'] = grouped[value_col]
    return grouped

# For time-block plots, need to keep the time_block dimension and plot with bars grouped by time_block
def make_timeblock_plot_frame(solution_df, value_col='n_new', route_filter=None, time_blocks=None, sort_routes_numeric=True):
    if value_col not in ['n_new', 'delta_n']:
        raise ValueError("value_col must be 'n_new' or 'delta_n'")

    df_plot = solution_df.copy()
    if route_filter is not None:
        df_plot = df_plot[df_plot['route'].isin(route_filter)].copy()

    if route_filter is not None:
        route_order = list(route_filter)
    else:
        route_vals = df_plot['route'].unique().tolist()
        route_order = sort_route_index(route_vals) if sort_routes_numeric else route_vals

    if time_blocks is None:
        timeblock_order = df_plot['time_block'].drop_duplicates().tolist()
    else:
        timeblock_order = [tb for tb in time_blocks if tb in df_plot['time_block'].unique()]

    plot_df = df_plot[['route', 'time_block', 'n_old', 'n_new', 'delta_n']].copy()
    plot_df['route'] = pd.Categorical(plot_df['route'], categories=route_order, ordered=True)
    plot_df['time_block'] = pd.Categorical(plot_df['time_block'], categories=timeblock_order, ordered=True)
    plot_df = plot_df.sort_values(['route', 'time_block']).reset_index(drop=True)
    plot_df['plot_value'] = plot_df[value_col]
    return plot_df, route_order, timeblock_order

# For sensitivity analysis, need to aggregate by both route and parameter value, and then pivot for plotting
def aggregate_sensitivity(solution_results, time_block='all', value_col='n_new'):
    if value_col not in ['n_new', 'delta_n']:
        raise ValueError("value_col must be 'n_new' or 'delta_n'")

    df_plot = solution_results.copy()
    if time_block != 'all':
        if time_block not in df_plot['time_block'].unique():
            raise ValueError(f'Unknown time_block: {time_block}')
        df_plot = df_plot[df_plot['time_block'] == time_block].copy()

    grouped = (
        df_plot.groupby(['route', 'parameter_value'], as_index=False)[['n_old', 'n_new', 'delta_n']]
        .sum()
    )
    return grouped

# For sensitivity analysis, need to aggregate by both route and parameter value, and then pivot for plotting
def make_sensitivity_plot_pivot(solution_results, time_block='all', value_col='n_new', route_filter=None, sort_routes_numeric=True):
    grouped = aggregate_sensitivity(solution_results=solution_results, time_block=time_block, value_col=value_col)

    if route_filter is not None:
        grouped = grouped[grouped['route'].isin(route_filter)].copy()

    pivot_value = grouped.pivot(index='route', columns='parameter_value', values=value_col)
    pivot_old = grouped.pivot(index='route', columns='parameter_value', values='n_old')
    pivot_delta = grouped.pivot(index='route', columns='parameter_value', values='delta_n')

    if route_filter is not None:
        target_index = list(route_filter)
    elif sort_routes_numeric:
        target_index = sort_route_index(pivot_value.index)
    else:
        target_index = list(pivot_value.index)

    return (
        pivot_value.reindex(target_index),
        pivot_old.reindex(target_index),
        pivot_delta.reindex(target_index),
    )

# Styling helper functions for bar plots (add baseline ticks and delta labels
def _style_single_bars(ax, plot_df, show_baseline_ticks=True, show_delta_labels=True, show_legend_baseline=True, color_bars_by_delta=True):
    baseline_handle_added = False
    for patch, (_, row) in zip(ax.patches, plot_df.iterrows()):
        x_left = patch.get_x()
        width = patch.get_width()
        x_mid = x_left + width / 2

        n_new_val = row['n_new']
        n_old_val = row['n_old']
        delta_val = row['delta_n']

        if color_bars_by_delta:
            if delta_val > 0:
                patch.set_facecolor('tab:green')
            elif delta_val < 0:
                patch.set_facecolor('tab:red')
            else:
                patch.set_facecolor('tab:gray')

        if show_baseline_ticks and pd.notna(n_old_val):
            tick_label = 'n_old baseline' if (show_legend_baseline and not baseline_handle_added) else '_nolegend_'
            ax.hlines(y=n_old_val, xmin=x_mid - width * 0.35, xmax=x_mid + width * 0.35, colors='black', linewidth=2, label=tick_label, zorder=4)
            if show_legend_baseline and not baseline_handle_added:
                baseline_handle_added = True

        if show_delta_labels and pd.notna(delta_val) and int(round(delta_val)) != 0:
            y_text = n_new_val + 0.15
            va = 'bottom'
            if n_new_val < 0:
                y_text = n_new_val - 0.15
                va = 'top'
            ax.text(x_mid, y_text, f'{int(round(delta_val)):+d}', ha='center', va=va, fontsize=8, zorder=5)

# Styling helper functions for grouped bar plots (add baseline ticks and delta labels for each bar in the group)
def _style_grouped_bars(ax, plot_df, show_baseline_ticks=True, show_delta_labels=True, show_legend_baseline=True):
    baseline_handle_added = False
    for patch, (_, row) in zip(ax.patches, plot_df.iterrows()):
        x_left = patch.get_x()
        width = patch.get_width()
        x_mid = x_left + width / 2

        n_new_val = row['n_new']
        n_old_val = row['n_old']
        delta_val = row['delta_n']

        if show_baseline_ticks and pd.notna(n_old_val):
            tick_label = 'n_old baseline' if (show_legend_baseline and not baseline_handle_added) else '_nolegend_'
            ax.hlines(y=n_old_val, xmin=x_mid - width * 0.35, xmax=x_mid + width * 0.35, colors='black', linewidth=2, label=tick_label, zorder=4)
            if show_legend_baseline and not baseline_handle_added:
                baseline_handle_added = True

        if show_delta_labels and pd.notna(delta_val) and int(round(delta_val)) != 0:
            y_text = n_new_val + 0.12 if n_new_val >= 0 else n_new_val - 0.12
            va = 'bottom' if n_new_val >= 0 else 'top'
            ax.text(x_mid, y_text, f'{int(round(delta_val)):+d}', ha='center', va=va, fontsize=7, rotation=90, zorder=5)

# Styling helper functions for sensitivity analysis bar plots (color bars by delta and add baseline ticks and delta labels for each bar in the group)
def _style_sensitivity_n_new_bars(ax, pivot_value, pivot_old, pivot_delta, show_baseline_ticks=True, show_delta_labels=True, show_legend_baseline=True, color_bars_by_delta=True):
    n_routes = len(pivot_value.index)
    n_series = len(pivot_value.columns)
    if n_routes == 0 or n_series == 0:
        return

    bars = ax.patches[: n_routes * n_series]
    baseline_handle_added = False

    for i, patch in enumerate(bars):
        route_idx = i % n_routes
        series_idx = i // n_routes

        route = pivot_value.index[route_idx]
        parameter_value = pivot_value.columns[series_idx]

        n_new_val = pivot_value.loc[route, parameter_value]
        n_old_val = pivot_old.loc[route, parameter_value]
        delta_val = pivot_delta.loc[route, parameter_value]

        if pd.isna(n_new_val):
            continue

        if color_bars_by_delta:
            if delta_val > 0:
                patch.set_facecolor('tab:green')
            elif delta_val < 0:
                patch.set_facecolor('tab:red')
            else:
                patch.set_facecolor('tab:gray')

        x_left = patch.get_x()
        width = patch.get_width()
        x_mid = x_left + width / 2

        if show_baseline_ticks and pd.notna(n_old_val):
            tick_label = 'n_old baseline' if (show_legend_baseline and not baseline_handle_added) else '_nolegend_'
            ax.hlines(y=n_old_val, xmin=x_mid - width * 0.35, xmax=x_mid + width * 0.35, colors='black', linewidth=2, label=tick_label, zorder=4)
            if show_legend_baseline and not baseline_handle_added:
                baseline_handle_added = True

        if show_delta_labels and pd.notna(delta_val) and int(round(delta_val)) != 0:
            y_text = n_new_val + 0.15 if n_new_val >= 0 else n_new_val - 0.15
            va = 'bottom' if n_new_val >= 0 else 'top'
            ax.text(x_mid, y_text, f'{int(round(delta_val)):+d}', ha='center', va=va, fontsize=8, zorder=5)

# Main plotting functions for single solution and sensitivity analysis, with options for all routes or selected routes, and time-block or overall plots
def plot_single_solution_all_routes(solution_df, time_block='all', value_col='n_new', time_blocks=None, figsize=(20, 8), sort_routes_numeric=True, show_baseline_ticks=True, show_delta_labels=True, show_legend_baseline=True, color_bars_by_delta=True):
    block_label, y_label = make_plot_labels(time_block=time_block, value_col=value_col)

    if time_block == 'all':
        plot_df, route_order, timeblock_order = make_timeblock_plot_frame(solution_df=solution_df, value_col=value_col, route_filter=None, time_blocks=time_blocks, sort_routes_numeric=sort_routes_numeric)
        pivot = plot_df.pivot(index='route', columns='time_block', values='plot_value').reindex(index=route_order, columns=timeblock_order)
        ax = pivot.plot(kind='bar', figsize=figsize)
        ax.set_title(f'All routes: {value_col} by route with time-block bars')
        ax.set_xlabel('Route')
        ax.set_ylabel(y_label)
        if value_col == 'delta_n':
            ax.axhline(0, linewidth=1)
        else:
            _style_grouped_bars(ax=ax, plot_df=plot_df, show_baseline_ticks=show_baseline_ticks, show_delta_labels=show_delta_labels, show_legend_baseline=show_legend_baseline)
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.show()
        return

    plot_df = make_plot_frame(solution_df=solution_df, time_block=time_block, value_col=value_col, route_filter=None, sort_routes_numeric=sort_routes_numeric)
    ax = plot_df.set_index('route')['plot_value'].plot(kind='bar', figsize=figsize)
    ax.set_title(f'All routes: {value_col} by route | {block_label}')
    ax.set_xlabel('Route')
    ax.set_ylabel(y_label)
    if value_col == 'delta_n':
        ax.axhline(0, linewidth=1)
    else:
        _style_single_bars(ax=ax, plot_df=plot_df, show_baseline_ticks=show_baseline_ticks, show_delta_labels=show_delta_labels, show_legend_baseline=show_legend_baseline, color_bars_by_delta=color_bars_by_delta)
        if show_legend_baseline:
            ax.legend()
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

# Similar to plot_single_solution_all_routes but only for selected routes of interest, and with option to not sort routes numerically (keep original order)
def plot_single_solution_selected_routes(solution_df, routes_of_interest, time_block='all', value_col='n_new', time_blocks=None, figsize=(12, 6), show_baseline_ticks=True, show_delta_labels=True, show_legend_baseline=True, color_bars_by_delta=True):
    block_label, y_label = make_plot_labels(time_block=time_block, value_col=value_col)

    if time_block == 'all':
        plot_df, route_order, timeblock_order = make_timeblock_plot_frame(solution_df=solution_df, value_col=value_col, route_filter=routes_of_interest, time_blocks=time_blocks, sort_routes_numeric=False)
        pivot = plot_df.pivot(index='route', columns='time_block', values='plot_value').reindex(index=route_order, columns=timeblock_order)
        ax = pivot.plot(kind='bar', figsize=figsize)
        ax.set_title(f'Selected routes: {value_col} by route with time-block bars')
        ax.set_xlabel('Route')
        ax.set_ylabel(y_label)
        if value_col == 'delta_n':
            ax.axhline(0, linewidth=1)
        else:
            _style_grouped_bars(ax=ax, plot_df=plot_df, show_baseline_ticks=show_baseline_ticks, show_delta_labels=show_delta_labels, show_legend_baseline=show_legend_baseline)
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.show()
        return

    plot_df = make_plot_frame(solution_df=solution_df, time_block=time_block, value_col=value_col, route_filter=routes_of_interest, sort_routes_numeric=False)
    ax = plot_df.set_index('route')['plot_value'].plot(kind='bar', figsize=figsize)
    ax.set_title(f'Selected routes: {value_col} by route | {block_label}')
    ax.set_xlabel('Route')
    ax.set_ylabel(y_label)
    if value_col == 'delta_n':
        ax.axhline(0, linewidth=1)
    else:
        _style_single_bars(ax=ax, plot_df=plot_df, show_baseline_ticks=show_baseline_ticks, show_delta_labels=show_delta_labels, show_legend_baseline=show_legend_baseline, color_bars_by_delta=color_bars_by_delta)
        if show_legend_baseline:
            ax.legend()
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()

# For sensitivity analysis, need to aggregate by both route and parameter value, and then pivot for plotting
def plot_sensitivity_all_routes(solution_results, parameter_name, time_block='all', value_col='n_new', figsize=(20, 8), sort_routes_numeric=True, show_baseline_ticks=True, show_delta_labels=True, show_legend_baseline=True, color_bars_by_delta=True):
    pivot_value, pivot_old, pivot_delta = make_sensitivity_plot_pivot(solution_results=solution_results, time_block=time_block, value_col=value_col, route_filter=None, sort_routes_numeric=sort_routes_numeric)
    block_label, y_label = make_plot_labels(time_block=time_block, value_col=value_col)

    ax = pivot_value.plot(kind='bar', figsize=figsize)
    ax.set_title(f'All routes: {value_col} by route | {block_label} | sensitivity: {parameter_name}')
    ax.set_xlabel('Route')
    ax.set_ylabel(y_label)
    if value_col == 'delta_n':
        ax.axhline(0, linewidth=1)
    else:
        _style_sensitivity_n_new_bars(ax=ax, pivot_value=pivot_value, pivot_old=pivot_old, pivot_delta=pivot_delta, show_baseline_ticks=show_baseline_ticks, show_delta_labels=show_delta_labels, show_legend_baseline=show_legend_baseline, color_bars_by_delta=color_bars_by_delta)
    ax.legend(title=parameter_name)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

# Similar to plot_sensitivity_all_routes but only for selected routes of interest, and with option to not sort routes numerically (keep original order)
def plot_sensitivity_selected_routes(solution_results, parameter_name, routes_of_interest, time_block='all', value_col='n_new', figsize=(10, 6), show_baseline_ticks=True, show_delta_labels=True, show_legend_baseline=True, color_bars_by_delta=True):
    pivot_value, pivot_old, pivot_delta = make_sensitivity_plot_pivot(solution_results=solution_results, time_block=time_block, value_col=value_col, route_filter=routes_of_interest, sort_routes_numeric=False)
    block_label, y_label = make_plot_labels(time_block=time_block, value_col=value_col)

    ax = pivot_value.plot(kind='bar', figsize=figsize)
    ax.set_title(f'Selected routes: {value_col} by route | {block_label} | sensitivity: {parameter_name}')
    ax.set_xlabel('Route')
    ax.set_ylabel(y_label)
    if value_col == 'delta_n':
        ax.axhline(0, linewidth=1)
    else:
        _style_sensitivity_n_new_bars(ax=ax, pivot_value=pivot_value, pivot_old=pivot_old, pivot_delta=pivot_delta, show_baseline_ticks=show_baseline_ticks, show_delta_labels=show_delta_labels, show_legend_baseline=show_legend_baseline, color_bars_by_delta=color_bars_by_delta)
    ax.legend(title=parameter_name)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()
