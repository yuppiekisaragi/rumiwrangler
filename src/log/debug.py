def debug_args(args):
    argsdict = vars(args)
    debug = 'RUMIWrangler launched with arguments:\n'
    for key, value in argsdict.items():
        debug += f'{key}: {value}\n'

    return debug
