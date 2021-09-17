# monkey-patch context to point to cc_disco_pie.json
from cookiecutter import generate
from cc_disco_pie.monkey_patch import generate_context_wrapper
generate.generate_context = generate_context_wrapper

# for use in tests need monkey-patched api main
from cookiecutter import cli
from cookiecutter import main as api_main 
main = cli.main


if __name__ == "__main__":
    main()