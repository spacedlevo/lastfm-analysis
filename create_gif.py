import imageio
import glob

def create_gif(filenames, duration):
    images = glob.glob('/home/levo/Documents/projects/lastfm/images/slides/*.png')
    for filename in filenames:
        images.append(imageio.imread(filename))
    output_file = 'Gif-%s.gif' % datetime.datetime.now().strftime('%Y-%M-%d-%H-%M-%S')
    imageio.mimsave(output_file, images, duration=duration)