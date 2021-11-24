import subprocess


def run():

    for pipeline_name in ["tycho", "aurora"]:
        subprocess.run(f"kedro run --pipeline {pipeline_name}")


if __name__ == "__main__":
    run()
