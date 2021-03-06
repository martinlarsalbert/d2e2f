import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.gridspec import GridSpec
from src.visualization import plot_ship
import imageio
import src.visualization

from ipywidgets import Layout, interact, IntSlider, interactive, Play
import ipywidgets as widgets
import os

def plot_thruster(ax, x,y,cos,sin, power, scale=20):
    
    l = power*scale
    ax.arrow(x=y, y=x, dx=-l*sin, dy=-l*cos, head_width=l/5, head_length=l/5)
    #ax.arrow(x=y, y=x, dx=l*sin, dy=-l*cos, head_width=l/5, head_length=l/5)

def plot_thrusters(ax,row,lpp=50, beam=20, scale=30, positions = ['SV','SE','NV','NE']):

    """
    Thruster 1 – NV
    Thruster 2 – SV
    Thruster 3 – NE
    Thruster 4 - SE
    """
    
    position_map = {
        'SV' : [-1,-1],
        'SE' : [-1,1],
        'NV' : [1,-1],
        'NE' : [1,1], 
    }

    ##As given by Anna:
    #positions = np.array([
    #    [1,-1],  # NV
    #    [-1,-1], # SV
    #    [1,1],   # NE
    #    [-1,1],  # SE
    #    
    #])
    #
    #Martins guess:
    positions_xy = np.array([position_map[position] for position in positions])
    
    coordinates = np.array([positions_xy[:,0]*lpp/2, positions_xy[:,1]*beam/2] ).T
    
    for i,position in enumerate(coordinates):
        
        n=i+1
        sin_key = 'sin_pm%i' % n
        cos_key = 'cos_pm%i' % n
        power_key = 'power_em_thruster_%i' % n
            
        plot_thruster(ax=ax, x=position[0], y=position[1], cos=row[cos_key], sin=row[sin_key], power=row[power_key], scale=scale)
        ax.text(position[1], position[0], ' Thruster %i' % n)

    # velocity
    l=row['sog']
    if row['reversing']:
        direction = np.deg2rad(row['cog'] - row['heading'] - 180)
    else:
        direction = np.deg2rad(row['cog'] - row['heading'])
        
    dx = l*np.cos(direction)
    dy = l*np.sin(direction)
    ax.arrow(x=0, y=0, dx=dy, dy=dx, head_width=l/5, head_length=l/5, color='green')
    ax.annotate(xy=(0,0), xytext=(1.3*dy,1.3*dx), text='velocity')
    
    
    ax.set_xlim(np.min(coordinates[:,1])-scale,np.max(coordinates[:,1])+scale)
    ax.set_ylim(np.min(coordinates[:,0])-scale,np.max(coordinates[:,0])+scale)
    #ax.set_aspect('equal', 'box')
    
    if row['reversing']:
        # Rotate the view
        ax.invert_yaxis()
        ax.invert_xaxis()
    
def plot_thrust_allocation(row, trip, lpp=50, beam=20, scale=30, positions = ['SV','SE','NV','NE']):
    
    #fig,axes=plt.subplots(ncols=2)
    fig = plt.figure(constrained_layout=True)
    fig.set_size_inches(19,8)
    
    gs = GridSpec(2, 2, figure=fig)
    ax1 = fig.add_subplot(gs[:, 0])
    # identical to ax1 = plt.subplot(gs.new_subplotspec((0, 0), colspan=3))
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1:, 1])
    
    ax = ax1
    
    plot_thrusters(ax=ax, row=row, lpp=lpp, beam=beam, scale=scale, positions=positions)
        
    ## Second plot:
    ax = ax2
    trip.plot(x='longitude', y='latitude', ax=ax, style='k--')
    #ax.plot(row['longitude'], row['latitude'], 'o', ms=15)
    x = row['latitude']
    y = row['longitude']
    psi = np.deg2rad(row['cog'])
    
    
    # Define a ship size in lat/lon:
    N_scale = 20
    lpp=50
    beam=20
    scale =  1/lpp/N_scale*np.sqrt((trip['latitude'].max() - trip['latitude'].min())**2 + (trip['longitude'].max() - trip['longitude'].min())**2)
    lpp_ = lpp*scale
    beam_ = beam*scale

    plot_ship.plot(x, y, psi, lpp = lpp_, beam = beam_, ax=ax, color='b', alpha=0.5)
    
    ax.set_ylim(trip['latitude'].min(), trip['latitude'].max())
    ax.set_xlim(trip['longitude'].min(), trip['longitude'].max())
    
    ax.set_aspect('equal')
    
    ## Third plot:
    trip.plot(x='trip_time_s', y='sog', ax=ax3, style='k--')
    ax3.plot(row['trip_time_s'], row['sog'], 'o', ms=15)
    ax3.set_xlabel('Time [s]')
    ax3.set_ylabel('Ship speed [m/s]')
    
def create_animator(trip, positions = ['SV','SE','NV','NE']):
    trip = trip.copy()
        
    def animate(i=0):
        
        index = int(i)
        row = trip.iloc[index]
        plot_thrust_allocation(row=row, trip=trip, positions=positions)
        
    return animate

def normalize_power(trip):
    trip=trip.copy()
    power_columns = ['power_em_thruster_%i' % i for i in range(1,5)]
    trip[power_columns]/=trip['power_em_thruster_total'].max()/4
    return trip


def widget(trip:pd.DataFrame, positions = ['SV','SE','NV','NE'])->widgets.VBox:
    """ipywidget widget stepping in the animation

    Parameters
    ----------
    trip : pd.DataFrame
        [description]

    Returns
    -------
    widget
        [description]
    """

    trip=trip.copy()

    ## Preprocess:
    trip['trip_time_s'] = pd.TimedeltaIndex(trip['trip_time']).total_seconds()

    ## Normalizing:
    trip = normalize_power(trip=trip)

    ## Resample:
    trip = trip.resample('2S').mean().dropna()

    animator = create_animator(trip=trip, positions=positions)

    play = Play(
    value=0,
    min=0,
    max=len(trip)-1,
    step=1,
    interval=100,
    description="Press play",
    disabled=False
    )

    slider = IntSlider(0,0,len(trip)-1,1, layout=Layout(width='70%'))
    widgets.jslink((play, 'value'), (slider, 'value'))
    animation = interactive(animator, i = slider); 
    return widgets.VBox([play, slider, animation])

def create_gif(trip:pd.DataFrame, animation_dir=None):
    """Create a GIF animation for a trip, showing the thrusters etc.

    Parameters
    ----------
    trip : pd.DataFrame
        [description]
    animation_dir : [type], optional
        [description], by default None
    """


    ## Where should the animation be placed?    
    if animation_dir is None:
        animation_dir = os.path.join(src.visualization.path, 'animations')
        if not os.path.exists(animation_dir):
            os.mkdir(animation_dir)
    
    file_paths = []
    trip_anim = trip.resample('5S').mean()
    
    ## Animate:
    for index, row in trip_anim.iterrows():
        plot_thrust_allocation(row=row)
        file_name = '%i.png' % row['trip_time_s']
        file_path = os.path.join(animation_dir, file_name)
        file_paths.append(file_path)
        plt.savefig(file_path)
        plt.close()

    ## Convert to GIF:
    trip_no = trip.iloc[0]['trip_no']
    save_file_path = os.path.join(animation_dir,'trip_%i.gif' % trip_no)
    with imageio.get_writer(save_file_path, mode='I') as writer:
        for file_path in file_paths:
            image = imageio.imread(file_path)
            writer.append_data(image)

    ## Clean up:
    for file_path in file_paths:
        os.remove(file_path)