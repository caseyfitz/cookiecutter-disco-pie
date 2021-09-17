from pathlib import Path

from cookiecutter.generate import generate_context


def generate_context_wrapper(*args, **kwargs):
    ''' Hardcoded in cookiecutter, so we override:
        https://github.com/cookiecutter/cookiecutter/blob/2bd62c67ec3e52b8e537d5346fd96ebd82803efe/cookiecutter/main.py#L85
    '''
    # replace full path to cookiecutter.json with full path to cc-disco-pie.json
    kwargs['context_file'] = str(Path(kwargs['context_file']).with_name('cc-disco-pie.json'))
    
    parsed_context = generate_context(*args, **kwargs)

    # replace key
    parsed_context['cookiecutter'] = parsed_context['cc-disco-pie']
    del parsed_context['cc-disco-pie']
    return parsed_context