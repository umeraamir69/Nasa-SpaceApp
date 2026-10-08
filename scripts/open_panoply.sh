#!/bin/zsh
# Launch Panoply with Java 21. Does not change enterprise Java 8 JAVA_HOME.
# Do not use `open -a Panoply` — the signed app follows JAVA_HOME=1.8 and fails.
set -e
export JAVA_HOME="/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
cd /Applications/Panoply.app/Contents/Java
exec "$JAVA_HOME/bin/java" -Xms256M -cp "*:." gov.nasa.giss.panoply.Panoply "$@"
