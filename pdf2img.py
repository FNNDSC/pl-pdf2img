#!/usr/bin/env python

from pathlib        import Path
from argparse       import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter

from                chris_plugin    import chris_plugin, PathMapper
from                pdf2image       import convert_from_path
from                PIL             import Image
from                tqdm            import tqdm
from                tqdm.contrib.concurrent import process_map
from                concurrent.futures  import ProcessPoolExecutor
import              os

__version__ = '1.0.0'

DISPLAY_TITLE = r'''

         dP                         dP .8888b d8888b. oo
         88                         88 88   "     `88
88d888b. 88          88d888b. .d888b88 88aaa  .aaadP' dP 88d8b.d8b. .d8888b.
88'  `88 88 88888888 88'  `88 88'  `88 88     88'     88 88'`88'`88 88'  `88
88.  .88 88          88.  .88 88.  .88 88     88.     88 88  88  88 88.  .88
88Y888P' dP          88Y888P' `88888P8 dP     Y88888P dP dP  dP  dP `8888P88
88                   88                                                  .88
dP                   dP                                              d8888P

'''

parser = ArgumentParser(description    ='''
A ChRIS DS Plugin that converts input PDF files to either jpg on png
output files.
''', formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('--outputType',
                    required   = False,
                    type        = str,
                    default     = 'jpg',
                    help        = 'Format of output image files')
parser.add_argument('--pattern',
                    default     = '**/*.pdf',
                    type        = str,
                    help        = 'input file filter glob')
parser.add_argument('-V', '--version', action='version',
                    version=f'%(prog)s {__version__}')

def env_check(options:Namespace) -> bool:
    if options.outputType not in ('jpg', 'jpeg', 'png'):
        raise ValueError("Output Type must be either jpg or png")
    return True

def pageIndex_insertIntoFileName(index:int, filename:Path) -> Path:
    fileWithIndex:Path          = filename.parent / Path(f'page-{index:03}-{filename.name}')
    return fileWithIndex

def pdf2img_convert(inputFile:Path, outputFile:Path) -> bool:
    images:list[Image.Image]    = convert_from_path(inputFile)
    for i, image in enumerate(images):
        outputWithPageIndex     = pageIndex_insertIntoFileName(i+1, outputFile)
        image.save(outputWithPageIndex)
    return True

def pdf2img_convertMap(io_tuple:tuple[Path,Path]) -> bool:
    inputFile, outputFile   = io_tuple
    return pdf2img_convert(inputFile, outputFile)

# The main function of this *ChRIS* plugin is denoted by this ``@chris_plugin`` "decorator."
# Some metadata about the plugin is specified here. There is more metadata specified in setup.py.
#
# documentation: https://fnndsc.github.io/chris_plugin/chris_plugin.html#chris_plugin
@chris_plugin(
    parser=parser,
    title='PDF to Image',
    category='',                 # ref. https://chrisstore.co/plugins
    min_memory_limit='100Mi',    # supported units: Mi, Gi
    min_cpu_limit='1000m',       # millicores, e.g. "1000m" = 1 CPU core
    min_gpu_limit=0              # set min_gpu_limit=1 to enable GPU
)
def main(options: Namespace, inputdir: Path, outputdir: Path):
    """
    *ChRIS* plugins usually have two positional arguments: an **input directory** containing
    input files and an **output directory** where to write output files. Command-line arguments
    are passed to this main method implicitly when ``main()`` is called below without parameters.

    :param options: non-positional arguments parsed by the parser given to @chris_plugin
    :param inputdir: directory containing (read-only) input files
    :param outputdir: directory where to write output files
    """

    print(DISPLAY_TITLE)

    # Typically it's easier to think of programs as operating on individual files
    # rather than directories. The helper functions provided by a ``PathMapper``
    # object make it easy to discover input files and write to output files inside
    # the given paths.
    #
    # Refer to the documentation for more options, examples, and advanced uses e.g.
    # adding a progress bar and parallelism.
    mapper:PathMapper   = PathMapper.file_mapper(inputdir, outputdir, glob=options.pattern, suffix = f'.{options.outputType}')
    max_workers:int     = os.cpu_count() or 1
    chunksize:int       = max(1, len(mapper) // max_workers)
    with ProcessPoolExecutor(max_workers = max_workers) as executor:
        process_map(pdf2img_convertMap, mapper, max_workers = max_workers, chunksize = chunksize)

if __name__ == '__main__':
    main()
