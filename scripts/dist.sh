#!/usr/bin/env bash

VERSION=$(cat VERSION)

rm -rf ./pkg/
mkdir -p ./pkg/dist

gox -output "pkg/{{.OS}}_{{.Arch}}/parkingspot"

echo "==> Packaging..."
for PLATFORM in $(find ./pkg -mindepth 1 -maxdepth 1 -type d); do
    OSARCH=$(basename ${PLATFORM})
    echo "--> ${OSARCH}"

    pushd $PLATFORM >/dev/null 2>&1
    zip ../dist/parkingspot-${VERSION}-${OSARCH}.zip ./*
    popd >/dev/null 2>&1
done

git commit -m "Version $(VERSION)"
git tag v$(VERSION) && git push --tags

github-release release --user acksin --repo parkingspot --tag v$(VERSION) --name "ParkingSpot $(VERSION)"

pushd pkg/dist

for f in $(find ./ -mindepth 1 -maxdepth 1 -type f); do
    github-release upload --user acksin --repo parkingspot --tag v$(VERSION) --name echo $(basename $f) --file $f
done
