import solara
import matplotlib.pyplot as plt
SEED = 42
from agents import *
from model import SymbioticRelationshipsModel
from matplotlib.patches import Rectangle
from mesa.experimental.devs import ABMSimulator


@solara.component
def CustomSpaceVisualization(model):
    """Custom space visualization with colored background zones"""
    # This is required to update the visualization when the model steps
    from mesa.visualization.components.matplotlib_components import update_counter
    update_counter.get()  # This triggers re-rendering on model updates
    # Setup figure
    fig = plt.Figure(figsize=(8, 8))    # Note: you must initialize a figure using this method instead of
    ax = fig.subplots()
    # set the width and height based on model
    width, height = model.width, model.height
    # Draw home area (light blue background)

    
   
    # Define nest areas
    for nest_location in model.spider_nests.values():
        start_nest_x = nest_location[0]
        start_nest_y = nest_location[1]
        nest = Rectangle((start_nest_x, start_nest_y), model.spider_nest_size, model.spider_nest_size,
                linewidth=0, facecolor='lightcoral', alpha=0.2)
        ax.add_patch(nest)
            # self.barcells.append(cell)
            
    # Draw our agents
    for frog in model.agents_by_type[Frog]:
        x, y = frog.cell.coordinate
        
        color = "tab:green"
        marker = "o"
        size = 100
        #     # Use matplotlib's OOP API instead of plt.scatter for thread safety
        ax.scatter(x + 0.5, y + 0.5, c=color, s=size, marker=marker, zorder=10, alpha=0.8)
        
    for spider in model.agents_by_type[Spider]:
        x, y = spider.cell.coordinate
        
        color = "tab:brown"
        marker = "X"
        size = 100
        #     # Use matplotlib's OOP API instead of plt.scatter for thread safety
        ax.scatter(x + 0.5, y + 0.5, c=color, marker=marker, s=size, zorder=10, alpha=0.8)
        
    for ant in model.agents_by_type[Ant]:
        x, y = ant.cell.coordinate
        
        color = "tab:red"
        marker = "d"
        size = 100
        #     # Use matplotlib's OOP API instead of plt.scatter for thread safety
        ax.scatter(x + 0.5, y + 0.5, c=color, marker=marker, s=size, zorder=10, alpha=0.8)
    
    for snake in model.agents_by_type[Snake]:
        x, y = snake.cell.coordinate
            
        color = "tab:orange"
        marker = "v"
        size = 100
        ax.scatter(x + 0.5, y + 0.5, c=color, marker=marker, s=size, zorder=10, alpha=0.8)

    try:
        for egg in model.agents_by_type[Egg]:
            x, y = egg.cell.coordinate
            
            color = "tab:blue"
            marker = "s"
            size = 100
            ax.scatter(x + 0.5, y + 0.5, c=color, marker=marker, s=size, zorder=10, alpha=0.8)
    except:
        pass

                
    # Set up the plot
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('X coordinate')
    ax.set_ylabel('Y coordinate')
    
    # This is required to render the visualization
    solara.FigureMatplotlib(fig)

# %%
from mesa.visualization import (
    CommandConsole,
    Slider,
    SolaraViz,
    make_plot_component,
    make_space_component,
)

if __name__ == '__main__':
    model_params = {
        "seed": {
            "type": "InputText",
            "value": SEED,
            "label": "Random Seed",
        },
        "initial_frogs": Slider("Initial Frog Population", 10, 1, 200),
        'initial_snakes': Slider("Initial Snake Population",10, 1, 200),
        "initial_ants" : Slider("Initial Ant Population",10, 1, 200),
        "p_reproduce_spider" : Slider("Spider Reproduction chance",0.04, 0, 1, step=0.01),
        "p_reproduce_snake" : Slider("Snake Reproduction chance",0.04, 0, 1, step=0.01),
        "p_reproduce_frog" : Slider("Frog Reproduction chance",0.04, 0, 1, step=0.01),
        "p_reproduce_ant" : Slider("Ant Reproduction chance",0.04, 0, 1, step=0.01),
        "grid_size" : Slider("Size of grid", 32, 32, 256, 4),
        "nest_density" : Slider("Nest density", 0.20, 0.1, 1, 0.05),
        "ant_spawn_rate" : Slider("Ant spawn per 2 ticks", 2, 1, 10),
    }

    def post_process_space(ax):
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])

    def post_process_lines(ax):
        ax.legend(loc="center left", bbox_to_anchor=(1, 0.9))

    simulator = ABMSimulator() 
    model = SymbioticRelationshipsModel(seed=SEED, initial_ants=10, initial_frogs=10, initial_snakes=10, nest_density=0.20, simulator=simulator)

    lineplot_component = make_plot_component(
        {"Frogs": "tab:green", "Spiders": "tab:brown","Snakes": "tab:orange","Ants":"tab:red"},
        post_process=post_process_lines,
    )

    lineplot_component2 = make_plot_component(
        {"Frog_Symb_Val": "tab:green", "Spider_Symb_Val": "tab:brown"},
        post_process=post_process_lines,
    )

    page = SolaraViz(
        model,
        # components=[space_component, lineplot_component, CommandConsole],
        components=[CustomSpaceVisualization, lineplot_component, lineplot_component2, CommandConsole],
        model_params=model_params,
        name="Symbiotic Relationships",
        simulator=simulator,
    )

    page  # noqa