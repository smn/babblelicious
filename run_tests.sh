#!/bin/bash

set -e

coverage erase
coverage run `which trial` babblelicious
coverage html
coverage report
