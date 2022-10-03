video jag följt :)
https://www.youtube.com/watch?v=GIF3LaRqgXo

Installera grejer innan användning

```python
pip
install
check - manifest
```

Hemma
google
cd C:/Users/lyamd/PycharmProjects/eunomia/lkpg_eunomia/
python setup.py bdist_wheel
python setup.py sdist
python setup.py bdist_wheel sdist

Skolans Dator
H:/Users/lyamd/PycharmProjects/eunomia/lkpg_eunomia/
python setup.py bdist_wheel
python setup.py sdist
python setup.py bdist_wheel sdist

# Installerar länk mellan koden och paketet som vi jobbar på

hemma:

cd C:/Users/lyamd/PycharmProjects/eunomia/lkpg_eunomia_pkg/
pip install -e .

På Skolan :

cd H:/Min enhet/Python/lkpg_eunomia/
pip install -e .