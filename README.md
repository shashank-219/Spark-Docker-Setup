**Spark on a Mac with Docker Compose**

Use these four files to start Spark locally, inspect the container, run a Python job, and open the Spark UI. Java, Python and Spark run inside Docker. The official `spark:4.2.1-python3` image supports Apple Silicon and Intel Macs. [Official Spark image](https://hub.docker.com/_/spark)

```text
~/Desktop/spark-local-setup/
├── README.md
├── compose.yaml
├── employees.csv
└── demo.py
```

**1. Install Docker Desktop**

Check Apple menu → About This Mac. Download Docker Desktop for your Apple M-series chip or Intel processor from [Docker’s Mac installation page](https://docs.docker.com/desktop/setup/install/mac-install/).

Move Docker to Applications, open it, and complete setup. Docker Desktop includes Compose. For this small example, a reasonable starting allocation is 2 CPUs and 4 GB of Docker memory, leaving enough memory for macOS.

Open your Mac Terminal and check:

```bash
docker --version
docker compose version
docker info
docker run --rm hello-world
```

`docker info` should show a Server section without a connection error. The last command should print “Hello from Docker!”

**2. Open the project folder**

Your four files are already in `~/Desktop/spark-local-setup`. Open your Mac Terminal and run:

```bash
cd ~/Desktop/spark-local-setup
ls
```

Run all Docker commands below from `~/Desktop/spark-local-setup`, where `compose.yaml` is located. If you open a new Terminal window, run the same `cd` command first.

The Compose file defines one service named `spark`. It uses the prebuilt Spark image, shares the CSV and Python file as read-only inputs, and maps the Spark UI to your Mac’s port 4040. Its startup command prints a message and keeps the container available for jobs.

**3. Start the container**

```bash
docker compose config --quiet
docker compose pull
docker compose up -d
```

The first command checks the configuration. The second downloads Spark. The third starts the container in the background. The first download may take a few minutes. [Compose startup](https://docs.docker.com/reference/cli/docker/compose/up/)

**4. Check the container**

```bash
docker compose ps
docker compose ps -a
```

Expect one service named `spark` with status `Up` and a port mapping containing `127.0.0.1:4040->4040/tcp`. `-a` also includes stopped containers. Running means the container is available; the sample job in step 7 checks that Spark actually works.

These equivalent Docker-level commands show containers across all projects:

```bash
docker ps
docker ps -a
```

Check this container’s resource use and processes:

```bash
docker stats --no-stream "$(docker compose ps -q spark)"
docker compose top spark
```

While idle, its processes include `sleep infinity`. Java and Python processes appear while a Spark job or session runs. [Compose process inspection](https://docs.docker.com/reference/cli/docker/compose/top/)

**5. Check startup logs**

```bash
docker compose logs --tail 50 spark
```

Expect `Spark container ready. Start PySpark or submit demo.py.`

To follow startup logs continuously:

```bash
docker compose logs -f spark
```

Press Control-C to stop following; the container keeps running. These logs belong to the container’s main process. Jobs launched with `exec` print their output in the terminal running that command. [Compose logs](https://docs.docker.com/reference/cli/docker/compose/logs/)

**6. Check inside the container**

```bash
docker compose exec spark python3 --version
docker compose exec spark java -version
docker compose exec spark /opt/spark/bin/spark-submit --version
docker compose exec spark ls -l /workspace
```

You should see Spark 4.2.1 and the two mounted files, `employees.csv` and `demo.py`.

For an interactive Linux shell:

```bash
docker compose exec spark bash
```

Inside that shell, try:

```bash
pwd
ls -l /workspace
exit
```

`exit` returns to your Mac Terminal without stopping the container. [Compose exec](https://docs.docker.com/reference/cli/docker/compose/exec/)

**7. Run the Spark job**

From your Mac Terminal:

```bash
docker compose exec spark /opt/spark/bin/spark-submit /workspace/demo.py
```

The job reads the CSV and calculates employee counts and average salaries by department. It runs in `local[2]` mode, meaning two worker threads inside this one container. [Spark local execution](https://spark.apache.org/docs/4.2.1/submitting-applications.html)

Expected result:

```text
+-----------+--------------+--------------+
| department|employee_count|average_salary|
+-----------+--------------+--------------+
|  Analytics|             1|       80000.0|
|Engineering|             2|      100000.0|
+-----------+--------------+--------------+
```

After the job finishes, the container stays running. Edit `demo.py` or `employees.csv` on your Mac and run the same command again to use your changes.

**8. Open PySpark and the Spark UI**

Once the job has finished, start an interactive session:

```bash
docker compose exec spark /opt/spark/bin/pyspark --master "local[2]"
```

At the Python `>>>` prompt, paste:

```python
spark.sparkContext.setLogLevel("WARN")
print(spark.version)

employees = spark.read.option("header", True).csv("/workspace/employees.csv")
employees.show()
print(employees.count())
```

You should see version `4.2.1`, the three employees, and a count of `3`.

Keep this session open and visit [Spark UI on localhost:4040](http://localhost:4040). You can inspect Jobs, Stages, SQL and Environment. The UI exists only while a Spark application is running; an idle container has no Spark UI. Run one Spark job or session at a time so it uses the published port. [Spark monitoring](https://spark.apache.org/docs/4.2.1/monitoring.html)

To leave PySpark, enter:

```python
exit()
```

The session and its UI close; the container stays running.

**9. Stop or restart**

Stop the container and confirm its status:

```bash
docker compose stop
docker compose ps -a
```

Start the same container again:

```bash
docker compose start
```

To stop and remove the project’s container and network:

```bash
docker compose down
```

Your four files remain on your Mac. To recreate the container later, run `docker compose up -d` again. [Compose shutdown](https://docs.docker.com/reference/cli/docker/compose/down/)

**10. Common fixes**

| Problem | Fix |
|---|---|
| `docker: command not found` | Finish Docker Desktop setup and reopen Terminal. |
| Cannot connect to Docker daemon | Open Docker Desktop and wait for it to start. |
| Compose configuration not found | Run `cd ~/Desktop/spark-local-setup` first. |
| Container exits unexpectedly | Run `docker compose ps -a` and `docker compose logs --tail 100 spark`. |
| Port 4040 already in use | In `compose.yaml`, change `127.0.0.1:4040:4040` to `127.0.0.1:4041:4040`, run `docker compose up -d`, then visit `localhost:4041`. |
| Spark UI unavailable | Keep PySpark open; wait for any other Spark job/session to finish first. |
| Input file not found | Keep both input files beside `compose.yaml`; use `/workspace/employees.csv` inside Spark. |
| Docker reports a mount permission error | Allow Docker access to `~/Desktop/spark-local-setup` in its file-sharing settings and allow access to Desktop if macOS prompts. |
| Container is killed or runs out of memory | Check `docker stats` and increase the memory available to Docker if needed. |
