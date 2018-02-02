# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import pytz
from collections import defaultdict
from tracker import get_model
from flask import Blueprint, redirect, render_template, request, url_for


crud = Blueprint('crud', __name__)

utc = pytz.utc
lax = pytz.timezone("America/Los_Angeles")

def add_time(data):
    now = datetime.datetime.utcnow()
    today = now.date()

    data['date'] = today.isoformat()
    data['time'] = now

    return data



# [START list]
@crud.route('/', methods=['GET', 'POST'])
def list():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        add_time(data)
        new_entry = get_model().create(data)
        return redirect(url_for('.list'))

    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    entries, next_page_token = get_model().list(cursor=token)

    for entry in entries:
        entry['time'] = entry['time'].astimezone(lax)

    return render_template(
        "list.html",
        entries=entries,
        next_page_token=next_page_token)
# [END list]


@crud.route('/<id>')
def view(id):
    entry = get_model().read(id)
    return render_template("view.html", entry=entry)


# [START add]
@crud.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        add_time(data)
        entry = get_model().create(data)

        return redirect(url_for('.view', id=entry['id']))

    return render_template("form.html", action="Add", book={})
# [END add]


@crud.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    entry = get_model().read(id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        add_time(data)
        entry = get_model().update(data, id)

        return redirect(url_for('.view', id=entry['id']))

    return render_template("form.html", action="Edit", entry=entry)


@crud.route('/<id>/delete')
def delete(id):
    get_model().delete(id)
    return redirect(url_for('.list'))
